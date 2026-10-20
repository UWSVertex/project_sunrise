from django import forms
from .models import Region, Country, Site, Location, Server, ServerMaintenance, ServerMonitoring
from django.utils import timezone

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., North America'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., NA'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name', 'code', 'region']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., US'}),
            'region': forms.Select(attrs={'class': 'form-select'}),
        }

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name', 'code', 'country', 'city', 'address', 'phone', 'contact_person', 'contact_email', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Site name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., NYC-DC1'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact person'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['site', 'name', 'location_type', 'row', 'number', 'capacity', 'notes']
        widgets = {
            'site': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location name'}),
            'location_type': forms.Select(attrs={'class': 'form-select'}),
            'row': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., A'}),
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 01'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'U height'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = [
            'name', 'serial_number', 'asset_tag', 'ip_address', 'hostname', 'mac_address',
            'site', 'location', 'rack_position', 'rack_units', 'server_type', 'status', 'environment',
            'os', 'os_version', 'description', 'domain', 'power_state', 'cpu_model', 'cpu_cores', 'cpu_threads',
            'memory_gb', 'storage_total_gb', 'storage_type', 'storage_info',
            'idrac_ip', 'idrac_username', 'idrac_password',
            'power_supply_count', 'network_interfaces', 'manufacturer', 'model',
            'warranty_vendor', 'server_po', 'windows_license_po',
            'purchase_date', 'warranty_expiry', 'last_maintenance', 'decommission_date',
            'assigned_to', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Server name'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_tag': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '192.168.1.1'}),
            'hostname': forms.TextInput(attrs={'class': 'form-control'}),
            'mac_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XX:XX:XX:XX:XX:XX'}),
            'site': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'server_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'environment': forms.Select(attrs={'class': 'form-select'}),
            'os': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Win 2019 Std, Rocky Linux 9, ESXi 7'}),
            'os_version': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., AD/DNS Primary'}),
            'domain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., LA.CONCENTRIX.COM'}),
            'power_state': forms.Select(attrs={'class': 'form-select'}),
            'cpu_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Intel Xeon E5-2698'}),
            'cpu_cores': forms.NumberInput(attrs={'class': 'form-control'}),
            'cpu_threads': forms.NumberInput(attrs={'class': 'form-control'}),
            'memory_gb': forms.NumberInput(attrs={'class': 'form-control'}),
            'storage_total_gb': forms.NumberInput(attrs={'class': 'form-control'}),
            'storage_type': forms.Select(attrs={'class': 'form-select'}),
            'storage_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'idrac_ip': forms.TextInput(attrs={'class': 'form-control'}),
            'idrac_username': forms.TextInput(attrs={'class': 'form-control'}),
            'idrac_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'power_supply_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'network_interfaces': forms.NumberInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Dell'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., PowerEdge R730'}),
            'warranty_vendor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Dell, HP, Relutech'}),
            'server_po': forms.TextInput(attrs={'class': 'form-control'}),
            'windows_license_po': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'last_maintenance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'decommission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_to': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Team or person'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        """Validate rack bay: must sit inside the rack and not overlap another server."""
        cleaned = super().clean()
        location = cleaned.get('location')
        pos = cleaned.get('rack_position')
        units = cleaned.get('rack_units') or 1

        if pos is None:
            return cleaned
        if not location:
            self.add_error('location', 'Pick a rack location before assigning a rack bay.')
            return cleaned

        height = location.capacity or 42
        if pos < 1 or pos + units - 1 > height:
            self.add_error('rack_position', f'Bay U{pos}-U{pos + units - 1} does not fit in a {height}U rack.')
            return cleaned

        wanted = set(range(pos, pos + units))
        others = Server.objects.filter(location=location, rack_position__isnull=False)
        if self.instance.pk:
            others = others.exclude(pk=self.instance.pk)
        for other in others:
            taken = set(range(other.rack_position, other.rack_position + (other.rack_units or 1)))
            if wanted & taken:
                self.add_error('rack_position', f'Overlaps {other.name} (U{other.rack_position}-U{other.rack_position + (other.rack_units or 1) - 1}).')
                break
        return cleaned


class ServerMaintenanceForm(forms.ModelForm):
    class Meta:
        model = ServerMaintenance
        fields = ['server', 'maintenance_type', 'description', 'performed_by', 'maintenance_date', 'next_maintenance_date', 'parts_replaced', 'notes']
        widgets = {
            'server': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'performed_by': forms.TextInput(attrs={'class': 'form-control'}),
            'maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'parts_replaced': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class ServerMonitoringForm(forms.ModelForm):
    class Meta:
        model = ServerMonitoring
        fields = ['server', 'is_monitored', 'monitoring_tool', 'health_status', 'cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 'cpu_warning_threshold', 'memory_warning_threshold', 'disk_warning_threshold', 'notes']
        widgets = {
            'server': forms.Select(attrs={'class': 'form-select'}),
            'is_monitored': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'monitoring_tool': forms.TextInput(attrs={'class': 'form-control'}),
            'health_status': forms.Select(attrs={'class': 'form-select'}),
            'cpu_usage_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'memory_usage_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'disk_usage_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'cpu_warning_threshold': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'memory_warning_threshold': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'disk_warning_threshold': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }



class RackForm(forms.ModelForm):
    """Rack = Location of type 'rack'. Type is fixed, not user-selectable."""
    class Meta:
        model = Location
        fields = ['site', 'name', 'capacity', 'notes']
        labels = {'capacity': 'Height (U)', 'name': 'Rack Name'}
        widgets = {
            'site': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Rack A01'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '42', 'min': 1}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        rack = super().save(commit=False)
        rack.location_type = 'rack'
        if not rack.capacity:
            rack.capacity = 42
        if commit:
            rack.save()
        return rack
