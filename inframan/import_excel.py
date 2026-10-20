"""
Excel bulk-import for Server inventory.

Matches the real inventory sheet's 22 columns:
  Country | Site | Server | IP Server | CrowdStrike... | Engineer Name |
  Patching Month... | Critical | Description | Domain | OS | VM \\ Physical |
  Status | Number of CPU | RAM | HDD Type [SSD/HDD] | Manufacturer / Model |
  Service Tag / Serial | iLO / iDRAC | Dell / HP / Relutech Warranty |
  Server PO | Windows License PO

Only Server Name, IP Address are required from the sheet. OS is free text
and imported as-is (model field has no fixed choices). Sites and Countries
are auto-created from the sheet's Country/Site columns if they don't exist
yet, since a real inventory file will reference many more sites than are
pre-registered.
"""
import re
import datetime
import openpyxl
from .models import Region, Country, Site, Server

REQUIRED_HEADERS_HELP = (
    "Expected columns (in order): Country, Site, Server, IP Server, "
    "CrowdStrike, Engineer Name, Patching Month, Critical, Description, "
    "Domain, OS, VM \\ Physical, Status, Number of CPU, RAM, "
    "HDD Type [SSD/HDD], Manufacturer / Model, Service Tag / Serial, "
    "iLO / iDRAC, Dell / HP / Relutech Warranty, Server PO, Windows License PO"
)

COLUMN_COUNT = 22

SERVER_TYPE_MAP = {
    'vm': 'virtual',
    'virtual': 'virtual',
    'virtual machine': 'virtual',
    'physical': 'physical',
    'blade': 'blade',
    'tower': 'tower',
}

POWER_STATE_MAP = {
    'powered on': 'powered_on',
    'powered off': 'powered_off',
    'on': 'powered_on',
    'off': 'powered_off',
}

STORAGE_TYPE_MAP = {
    'ssd': 'ssd',
    'hdd': 'hdd',
    'nvme': 'nvme',
}

BLANK_MARKERS = {'', '-', 'n/a', 'na', 'none', '\xa0'}

UNASSIGNED_REGION_NAME = 'Unassigned (Auto-Created)'
UNASSIGNED_REGION_CODE = 'AUTO'


def _clean(value):
    if value is None:
        return ''
    if isinstance(value, datetime.datetime):
        return value.strftime('%Y-%m-%d')
    text = str(value).strip()
    if not text:
        return ''
    # Treat any run of only dashes/placeholder punctuation as blank (sheets use '-', '--', etc.)
    if re.fullmatch(r'[-–—]+', text):
        return ''
    return '' if text.lower() in BLANK_MARKERS else text


def _parse_int(value):
    """Pull the first integer out of strings like '8 Processors' or '32 GB', or pass through a raw number."""
    if isinstance(value, (int, float)):
        return int(value)
    text = _clean(value)
    if not text:
        return None
    match = re.search(r'\d+', text.replace(',', ''))
    return int(match.group()) if match else None


def _detect_storage_type(hdd_text):
    text = hdd_text.lower()
    if 'ssd' in text:
        return 'ssd'
    if 'nvme' in text:
        return 'nvme'
    if 'hdd' in text or 'sas' in text:
        return 'hdd'
    return None


def _split_manufacturer_model(text):
    """'Dell PowerEdge R440' -> ('Dell', 'PowerEdge R440'); falls back to (None, text)."""
    if not text:
        return None, None
    known_makers = ['Dell', 'HP', 'HPE', 'Lenovo', 'Supermicro', 'Cisco', 'IBM', 'Hitachi']
    for maker in known_makers:
        if text.lower().startswith(maker.lower()):
            rest = text[len(maker):].strip()
            return maker, rest or None
    return None, text


def _get_or_create_region(cache):
    if 'region' not in cache:
        region, _ = Region.objects.get_or_create(
            code=UNASSIGNED_REGION_CODE,
            defaults={'name': UNASSIGNED_REGION_NAME, 'description': 'Auto-created during Excel import.'}
        )
        cache['region'] = region
    return cache['region']


def _get_or_create_country(country_name, cache):
    if not country_name:
        return None
    key = country_name.lower()
    if key not in cache.setdefault('countries', {}):
        country = Country.objects.filter(name__iexact=country_name).first()
        if not country:
            region = _get_or_create_region(cache)
            code = re.sub(r'[^A-Za-z]', '', country_name)[:5].upper() or 'XX'
            # Ensure uniqueness of the generated code
            base_code, n = code, 1
            while Country.objects.filter(code=code).exists():
                n += 1
                code = f'{base_code[:4]}{n}'
            country = Country.objects.create(name=country_name, code=code, region=region)
        cache['countries'][key] = country
    return cache['countries'][key]


def _get_or_create_site(site_name, country, cache):
    if not site_name:
        return None
    key = site_name.lower()
    if key not in cache.setdefault('sites', {}):
        site = Site.objects.filter(name__iexact=site_name).first() or Site.objects.filter(code__iexact=site_name).first()
        if not site and country:
            base_code = re.sub(r'[^A-Za-z0-9]', '', site_name)[:16].upper() or 'SITE'
            code, n = base_code, 1
            while Site.objects.filter(code=code).exists():
                n += 1
                code = f'{base_code[:14]}{n}'
            site = Site.objects.create(name=site_name, code=code, country=country, city=site_name)
        cache['sites'][key] = site
    return cache['sites'][key]


def parse_workbook(file_obj, auto_create_sites=True):
    """
    Parse the uploaded .xlsx file into a list of row dicts, each annotated
    with 'errors' (list of str) and 'warnings' (list of str), plus flags
    indicating whether a Site/Country will be newly created.
    When auto_create_sites is True, missing Sites/Countries are created as
    this function runs (so repeated calls are idempotent after the first).
    """
    wb = openpyxl.load_workbook(file_obj, data_only=True)
    sheet = wb.active

    results = []
    existing_ips = set(Server.objects.values_list('ip_address', flat=True))
    existing_names = set(Server.objects.values_list('name', flat=True))
    existing_serials = set(Server.objects.exclude(serial_number__isnull=True).exclude(serial_number='').values_list('serial_number', flat=True))
    seen_ips_in_file = set()
    seen_names_in_file = set()
    seen_serials_in_file = set()
    cache = {}

    header_skipped = False

    for row_idx, row in enumerate(sheet.iter_rows(min_row=1, values_only=True), start=1):
        if row is None or all(cell is None or _clean(cell) == '' for cell in row):
            continue  # skip fully blank rows

        # Skip the header row if present (first cell looks like a label, not data)
        if not header_skipped:
            header_skipped = True
            first_cell = _clean(row[0]) if row else ''
            if first_cell.lower() in ('country',):
                continue

        padded = list(row) + [None] * (COLUMN_COUNT - len(row))
        (country_raw, site_raw, name, ip_address, _crowdstrike, _engineer, _patching,
         _critical, description, domain, os_raw, vmphys_raw, status_raw, cpu_raw,
         ram_raw, hdd_raw, mfgmodel_raw, serial, idrac_ip, warranty_raw,
         server_po, windows_license_po) = padded[:COLUMN_COUNT]

        country_name = _clean(country_raw)
        site_name = _clean(site_raw)
        name = _clean(name)
        ip_address = _clean(ip_address)
        description = _clean(description)
        domain = _clean(domain)
        os_value = _clean(os_raw)
        serial = _clean(serial)
        idrac_ip = _clean(idrac_ip)
        warranty_raw_clean = _clean(warranty_raw)
        server_po = _clean(server_po)
        windows_license_po = _clean(windows_license_po)
        hdd_text = _clean(hdd_raw)
        mfgmodel_text = _clean(mfgmodel_raw)

        errors = []
        warnings = []

        if not name:
            errors.append('Server Name is required.')
        elif name in existing_names or name in seen_names_in_file:
            errors.append(f'A server named "{name}" already exists or is duplicated in this file.')

        if not ip_address:
            errors.append('IP Address is required.')
        elif ip_address in existing_ips or ip_address in seen_ips_in_file:
            errors.append(f'IP address "{ip_address}" already exists or is duplicated in this file.')

        serial_conflict = False
        if serial and (serial in existing_serials or serial in seen_serials_in_file):
            warnings.append(f'Serial number "{serial}" already exists or is duplicated in this file; it will be left blank for this row.')
            serial_conflict = True

        site = None
        site_is_new = False
        country_is_new = False
        if site_name:
            existing_site = Site.objects.filter(name__iexact=site_name).first() or Site.objects.filter(code__iexact=site_name).first()
            site_is_new = existing_site is None
            country = None
            if country_name:
                country_is_new = not Country.objects.filter(name__iexact=country_name).exists()
            if auto_create_sites:
                country = _get_or_create_country(country_name, cache) if country_name else None
                site = _get_or_create_site(site_name, country, cache)
                if site is None and not country_name:
                    errors.append(f'Site "{site_name}" does not exist and no Country was given to auto-create it.')
            else:
                site = existing_site
                if not site:
                    errors.append(f'No site found named "{site_name}". Create it first or enable auto-create.')
        else:
            errors.append('Site is required to link this server to a location.')

        server_type = SERVER_TYPE_MAP.get(_clean(vmphys_raw).lower(), 'physical')
        if _clean(vmphys_raw) and _clean(vmphys_raw).lower() not in SERVER_TYPE_MAP:
            warnings.append(f'Unrecognized server type "{vmphys_raw}", defaulted to Physical.')

        power_state = POWER_STATE_MAP.get(_clean(status_raw).lower(), 'unknown')

        cpu_cores = _parse_int(cpu_raw)
        memory_gb = _parse_int(ram_raw)
        storage_type = _detect_storage_type(hdd_text)
        manufacturer, model = _split_manufacturer_model(mfgmodel_text)

        if not errors:
            seen_names_in_file.add(name)
            seen_ips_in_file.add(ip_address)
            if serial and not serial_conflict:
                seen_serials_in_file.add(serial)

        results.append({
            'row': row_idx,
            'country': country_name,
            'country_is_new': country_is_new,
            'site_name': site_name,
            'site_id': site.pk if site else None,
            'site_display': str(site) if site else (site_name or '—'),
            'site_is_new': site_is_new,
            'name': name,
            'ip_address': ip_address,
            'description': description,
            'domain': domain,
            'os': os_value or None,
            'server_type': server_type,
            'power_state': power_state,
            'cpu_cores': cpu_cores,
            'memory_gb': memory_gb,
            'storage_info': hdd_text or None,
            'storage_type': storage_type,
            'manufacturer': manufacturer,
            'model': model,
            'serial_number': None if serial_conflict else (serial or None),
            'idrac_ip': idrac_ip or None,
            'warranty_vendor': warranty_raw_clean or None,
            'server_po': server_po or None,
            'windows_license_po': windows_license_po or None,
            'errors': errors,
            'warnings': warnings,
        })

    return results


def create_servers_from_rows(rows):
    """Bulk-create Server records from previously-validated row dicts (no errors).
    Wrapped in a single transaction so a late failure (e.g. an unexpected
    constraint violation) rolls back everything instead of leaving a partial
    import committed.
    """
    from django.db import transaction
    created = []
    with transaction.atomic():
        for row in rows:
            if row.get('errors'):
                continue
            server = Server.objects.create(
                name=row['name'],
                ip_address=row['ip_address'],
                site_id=row['site_id'],
                os=row['os'] or 'Unknown',
                description=row['description'] or None,
                domain=row['domain'] or None,
                server_type=row['server_type'],
                power_state=row['power_state'],
                cpu_cores=row['cpu_cores'],
                memory_gb=row['memory_gb'],
                storage_info=row['storage_info'],
                storage_type=row['storage_type'] or 'ssd',
                manufacturer=row['manufacturer'],
                model=row['model'],
                serial_number=row['serial_number'],
                idrac_ip=row['idrac_ip'],
                warranty_vendor=row['warranty_vendor'],
                server_po=row['server_po'],
                windows_license_po=row['windows_license_po'],
            )
            created.append(server)
    return created
