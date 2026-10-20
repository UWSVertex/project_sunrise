from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Region, Country, Site, Location, Server, ServerMaintenance, ServerMonitoring
from .forms import RegionForm, CountryForm, SiteForm, LocationForm, ServerForm, ServerMaintenanceForm, ServerMonitoringForm, RackForm

# ===== INFRASTRUCTURE DASHBOARD =====

def infrastructure_dashboard(request):
    """Infrastructure management dashboard"""
    context = {
        'total_servers': Server.objects.count(),
        'production_servers': Server.objects.filter(environment='production').count(),
        'spare_servers': Server.objects.filter(environment='spare').count(),
        'maintenance_servers': Server.objects.filter(status='maintenance').count(),
        'total_sites': Site.objects.count(),
        'total_regions': Region.objects.count(),
        'recent_servers': Server.objects.order_by('-created_at')[:5],
        'recent_maintenance': ServerMaintenance.objects.order_by('-maintenance_date')[:5],
    }
    return render(request, 'inframan/dashboard.html', context)

# ===== REGION VIEWS =====

def region_list(request):
    regions = Region.objects.all()
    return render(request, 'inframan/region_list.html', {'regions': regions})

def region_create(request):
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    if request.method == 'POST':
        form = RegionForm(request.POST)
        if form.is_valid():
            region = form.save()
            messages.success(request, f'Region {region.name} created.')
            if next_url.startswith('/infrastructure/'):
                sep = '&' if '?' in next_url else '?'
                return redirect(f'{next_url}{sep}region={region.pk}')
            return redirect('inframan:region_list')
    else:
        form = RegionForm()
    return render(request, 'inframan/region_form.html', {
        'form': form, 'title': 'Create Region', 'next': next_url,
    })

def region_edit(request, pk):
    region = get_object_or_404(Region, pk=pk)
    if request.method == 'POST':
        form = RegionForm(request.POST, instance=region)
        if form.is_valid():
            form.save()
            messages.success(request, 'Region updated successfully!')
            return redirect('inframan:region_list')
    else:
        form = RegionForm(instance=region)
    return render(request, 'inframan/region_form.html', {'form': form, 'region': region, 'title': 'Edit Region'})

def region_delete(request, pk):
    region = get_object_or_404(Region, pk=pk)
    if request.method == 'POST':
        region.delete()
        messages.success(request, 'Region deleted successfully!')
        return redirect('inframan:region_list')
    return render(request, 'inframan/confirm_delete.html', {'object': region, 'type': 'Region'})

# ===== SERVER VIEWS =====

def server_list(request):
    """List all servers with filtering"""
    servers = Server.objects.all().select_related('site', 'location').order_by('name')
    
    status_filter = request.GET.get('status')
    environment_filter = request.GET.get('environment')
    site_filter = request.GET.get('site')
    
    if status_filter:
        servers = servers.filter(status=status_filter)
    if environment_filter:
        servers = servers.filter(environment=environment_filter)
    if site_filter:
        servers = servers.filter(site_id=site_filter)
    
    sites = Site.objects.all()
    
    return render(request, 'inframan/server_list.html', {
        'servers': servers,
        'sites': sites,
        'status_filter': status_filter,
        'environment_filter': environment_filter,
        'site_filter': site_filter,
    })

def server_detail(request, pk):
    """Server detail view"""
    server = get_object_or_404(Server, pk=pk)
    maintenance_records = server.maintenance_records.all()
    monitoring = server.monitoring if hasattr(server, 'monitoring') else None
    
    return render(request, 'inframan/server_detail.html', {
        'server': server,
        'maintenance_records': maintenance_records,
        'monitoring': monitoring,
    })

def server_create(request):
    """Create new server"""
    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            server = form.save()
            # Auto-create monitoring record
            ServerMonitoring.objects.get_or_create(server=server)
            messages.success(request, f'Server "{server.name}" created successfully!')
            return redirect('inframan:server_detail', pk=server.pk)
    else:
        form = ServerForm()
    return render(request, 'inframan/server_form.html', {'form': form, 'title': 'Add New Server'})

def server_edit(request, pk):
    """Edit server"""
    server = get_object_or_404(Server, pk=pk)
    if request.method == 'POST':
        form = ServerForm(request.POST, instance=server)
        if form.is_valid():
            form.save()
            messages.success(request, f'Server "{server.name}" updated successfully!')
            return redirect('inframan:server_detail', pk=server.pk)
    else:
        form = ServerForm(instance=server)
    return render(request, 'inframan/server_form.html', {'form': form, 'server': server, 'title': 'Edit Server'})

def server_delete(request, pk):
    """Delete server"""
    server = get_object_or_404(Server, pk=pk)
    if request.method == 'POST':
        server_name = server.name
        server.delete()
        messages.success(request, f'Server "{server_name}" deleted successfully!')
        return redirect('inframan:server_list')
    return render(request, 'inframan/confirm_delete.html', {'object': server, 'type': 'Server'})

# ===== SITE VIEWS =====

def site_list(request):
    """List all sites"""
    sites = Site.objects.select_related('country', 'country__region').all()
    return render(request, 'inframan/site_list.html', {'sites': sites})

def site_detail(request, pk):
    """Site detail with servers"""
    site = get_object_or_404(Site, pk=pk)
    servers = site.servers.all()
    locations = site.locations.all()
    
    return render(request, 'inframan/site_detail.html', {
        'site': site,
        'servers': servers,
        'locations': locations,
    })

def site_create(request):
    """Create new site"""
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site created successfully!')
            return redirect('inframan:site_list')
    else:
        initial = {}
        if request.GET.get('country'):
            initial['country'] = request.GET.get('country')
        form = SiteForm(initial=initial)
    return render(request, 'inframan/site_form.html', {'form': form, 'title': 'Create Site'})

def site_edit(request, pk):
    """Edit site"""
    site = get_object_or_404(Site, pk=pk)
    if request.method == 'POST':
        form = SiteForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site updated successfully!')
            return redirect('inframan:site_detail', pk=site.pk)
    else:
        form = SiteForm(instance=site)
    return render(request, 'inframan/site_form.html', {'form': form, 'site': site, 'title': 'Edit Site'})

# ===== MAINTENANCE VIEWS =====

def maintenance_list(request):
    """List maintenance records"""
    records = ServerMaintenance.objects.select_related('server').order_by('-maintenance_date')
    return render(request, 'inframan/maintenance_list.html', {'records': records})

def maintenance_create(request):
    """Create maintenance record"""
    if request.method == 'POST':
        form = ServerMaintenanceForm(request.POST)
        if form.is_valid():
            maintenance = form.save()
            # Update server's last_maintenance
            maintenance.server.last_maintenance = maintenance.maintenance_date
            maintenance.server.save()
            messages.success(request, 'Maintenance record created successfully!')
            return redirect('inframan:maintenance_list')
    else:
        form = ServerMaintenanceForm()
    return render(request, 'inframan/maintenance_form.html', {'form': form, 'title': 'Record Maintenance'})


def rack_detail(request, pk):
    """Visual rack elevation: U slots from top to bottom with servers placed in their bays"""
    location = get_object_or_404(Location, pk=pk)
    height = location.capacity or 42
    servers = list(location.servers.all())

    # Map each U slot to the server occupying it
    slot_map = {}
    unassigned = []
    for srv in servers:
        if srv.rack_position:
            for u in range(srv.rack_position, srv.rack_position + (srv.rack_units or 1)):
                slot_map[u] = srv
        else:
            unassigned.append(srv)

    # Build rows from top (height) to bottom (1)
    rows = []
    u = height
    while u >= 1:
        srv = slot_map.get(u)
        if srv and srv.rack_position == u:
            span = srv.rack_units or 1
            rows.append({'u': u, 'server': srv, 'span': span, 'empty': False})
            u -= span
        elif srv:
            u -= 1  # continuation slot, already covered by the block above
        else:
            rows.append({'u': u, 'server': None, 'span': 1, 'empty': True})
            u -= 1

    return render(request, 'inframan/rack_detail.html', {
        'location': location,
        'height': height,
        'rows': rows,
        'unassigned': unassigned,
        'placed': sorted([s for s in servers if s.rack_position], key=lambda s: -s.rack_position),
        'used_units': sum(s.rack_units or 1 for s in servers if s.rack_position),
    })


def rack_list(request):
    """All racks (Location records of type rack) with placed-unit counts"""
    racks = Location.objects.filter(location_type='rack').select_related('site').order_by('site__name', 'name')
    rack_rows = []
    for rack in racks:
        servers = list(rack.servers.all())
        used = sum(s.rack_units or 1 for s in servers if s.rack_position)
        height = rack.capacity or 42
        rack_rows.append({
            'rack': rack,
            'height': height,
            'used': used,
            'free': max(height - used, 0),
            'server_count': len(servers),
        })
    return render(request, 'inframan/rack_list.html', {'rack_rows': rack_rows})


def rack_create(request):
    """Create a new rack (Location of type rack)"""
    if request.method == 'POST':
        form = RackForm(request.POST)
        if form.is_valid():
            rack = form.save()
            messages.success(request, f'Rack {rack.name} created.')
            return redirect('inframan:rack_detail', pk=rack.pk)
    else:
        form = RackForm()
    return render(request, 'inframan/rack_form.html', {'form': form, 'title': 'Create Rack'})


def country_create(request):
    """Create a country; optionally return to the site form that requested it."""
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    if request.method == 'POST':
        form = CountryForm(request.POST)
        if form.is_valid():
            country = form.save()
            messages.success(request, f'Country {country.name} created.')
            if next_url.startswith('/infrastructure/'):
                sep = '&' if '?' in next_url else '?'
                return redirect(f'{next_url}{sep}country={country.pk}')
            return redirect('inframan:region_list')
    else:
        initial = {}
        if request.GET.get('region'):
            initial['region'] = request.GET.get('region')
        form = CountryForm(initial=initial)
    return render(request, 'inframan/country_form.html', {
        'form': form, 'title': 'Create Country', 'next': next_url,
    })

def country_list(request):
    """All countries with their region and site counts"""
    countries = Country.objects.select_related('region').all()
    return render(request, 'inframan/country_list.html', {'countries': countries})

def country_edit(request, pk):
    """Edit a country"""
    country = get_object_or_404(Country, pk=pk)
    if request.method == 'POST':
        form = CountryForm(request.POST, instance=country)
        if form.is_valid():
            form.save()
            messages.success(request, f'Country "{country.name}" updated successfully!')
            return redirect('inframan:country_list')
    else:
        form = CountryForm(instance=country)
    return render(request, 'inframan/country_form.html', {'form': form, 'title': 'Edit Country', 'next': ''})

def country_delete(request, pk):
    """Delete a country"""
    from django.db.models import ProtectedError
    country = get_object_or_404(Country, pk=pk)
    if request.method == 'POST':
        country_name = country.name
        try:
            country.delete()
            messages.success(request, f'Country "{country_name}" deleted successfully!')
        except ProtectedError:
            messages.error(request, f'Cannot delete "{country_name}" while it still has sites linked to it.')
        return redirect('inframan:country_list')
    return render(request, 'inframan/confirm_delete.html', {'object': country, 'type': 'Country'})


# ===== EXCEL IMPORT =====
import os
import uuid
from django.conf import settings
from .import_excel import parse_workbook, create_servers_from_rows, REQUIRED_HEADERS_HELP

IMPORT_TMP_DIR = os.path.join(settings.MEDIA_ROOT, 'server_imports')


def server_import_upload(request):
    """Step 1: upload an .xlsx file and preview parsed rows before committing."""
    if request.method == 'POST' and request.FILES.get('excel_file'):
        uploaded = request.FILES['excel_file']
        if not uploaded.name.lower().endswith('.xlsx'):
            messages.error(request, 'Please upload a .xlsx file.')
            return redirect('inframan:server_import_upload')

        os.makedirs(IMPORT_TMP_DIR, exist_ok=True)
        token = uuid.uuid4().hex
        tmp_path = os.path.join(IMPORT_TMP_DIR, f'{token}.xlsx')
        with open(tmp_path, 'wb') as dest:
            for chunk in uploaded.chunks():
                dest.write(chunk)

        try:
            rows = parse_workbook(tmp_path)
        except Exception as exc:
            os.remove(tmp_path)
            messages.error(request, f'Could not read that file: {exc}')
            return redirect('inframan:server_import_upload')

        if not rows:
            os.remove(tmp_path)
            messages.warning(request, 'No data rows found in that file.')
            return redirect('inframan:server_import_upload')

        valid_count = sum(1 for r in rows if not r['errors'])
        error_count = len(rows) - valid_count

        return render(request, 'inframan/server_import_preview.html', {
            'rows': rows,
            'token': token,
            'valid_count': valid_count,
            'error_count': error_count,
        })

    return render(request, 'inframan/server_import_upload.html', {
        'help_text': REQUIRED_HEADERS_HELP,
    })


def server_import_confirm(request, token):
    """Step 2: re-parse the stashed file (guards against stale/tampered data) and bulk-create."""
    tmp_path = os.path.join(IMPORT_TMP_DIR, f'{token}.xlsx')
    if request.method != 'POST' or not os.path.exists(tmp_path):
        messages.error(request, 'That import session has expired. Please upload the file again.')
        return redirect('inframan:server_import_upload')

    rows = parse_workbook(tmp_path)
    created = create_servers_from_rows(rows)

    for server in created:
        ServerMonitoring.objects.get_or_create(server=server)

    os.remove(tmp_path)

    skipped = len(rows) - len(created)
    if created:
        messages.success(request, f'Imported {len(created)} server(s).' + (f' Skipped {skipped} row(s) with errors.' if skipped else ''))
    else:
        messages.error(request, 'No servers were imported; every row had errors.')

    return redirect('inframan:server_list')


def server_import_cancel(request, token):
    """Discard a pending import without creating anything."""
    tmp_path = os.path.join(IMPORT_TMP_DIR, f'{token}.xlsx')
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    messages.info(request, 'Import cancelled.')
    return redirect('inframan:server_list')


def server_bulk_delete(request):
    """Delete multiple servers selected via checkboxes on the server list."""
    if request.method == 'POST':
        ids = request.POST.getlist('server_ids')
        if ids:
            qs = Server.objects.filter(pk__in=ids)
            count = qs.count()
            qs.delete()
            messages.success(request, f'Deleted {count} server(s).')
        else:
            messages.warning(request, 'No servers were selected.')
    return redirect('inframan:server_list')
