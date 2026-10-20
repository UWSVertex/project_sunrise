from django.db import models
from django.utils import timezone

# ===== LOCATION & SITE MODELS =====

class Region(models.Model):
    """Geographic region (e.g., North America, Europe, Asia)"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'
    
    def __str__(self):
        return self.name


class Country(models.Model):
    """Country within a region"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=5, unique=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name='countries')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
    
    def __str__(self):
        return f"{self.name} ({self.region.code})"


class Site(models.Model):
    """Physical site/data center location"""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=20, unique=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='sites')
    city = models.CharField(max_length=100)
    
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Site'
        verbose_name_plural = 'Sites'
    
    def __str__(self):
        return f"{self.name} ({self.country.name})"


class Location(models.Model):
    """Specific location within a site (e.g., Rack, Room)"""
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=100)
    location_type = models.CharField(
        max_length=20,
        choices=[
            ('rack', 'Rack'),
            ('room', 'Room'),
            ('cabinet', 'Cabinet'),
            ('cage', 'Cage'),
            ('other', 'Other'),
        ],
        default='rack'
    )
    
    row = models.CharField(max_length=20, blank=True, null=True)
    number = models.CharField(max_length=20, blank=True, null=True)
    
    capacity = models.IntegerField(blank=True, null=True, help_text="Number of U height")
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['site', 'name']
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
    
    def __str__(self):
        return f"{self.site.name} - {self.name}"


# ===== SERVER MODELS =====

SERVER_STATUS_CHOICES = [
    ('active', 'Active'),
    ('maintenance', 'Maintenance'),
    ('decommissioned', 'Decommissioned'),
    ('spare', 'Spare'),
]

SERVER_ENVIRONMENT_CHOICES = [
    ('production', 'Production'),
    ('staging', 'Staging'),
    ('development', 'Development'),
    ('testing', 'Testing'),
    ('backup', 'Backup'),
    ('spare', 'Spare'),
]

OS_CHOICES = [
    ('windows_server_2016', 'Windows Server 2016'),
    ('windows_server_2019', 'Windows Server 2019'),
    ('windows_server_2022', 'Windows Server 2022'),
    ('rhel_7', 'RHEL 7'),
    ('rhel_8', 'RHEL 8'),
    ('rhel_9', 'RHEL 9'),
    ('centos_7', 'CentOS 7'),
    ('ubuntu_18', 'Ubuntu 18.04 LTS'),
    ('ubuntu_20', 'Ubuntu 20.04 LTS'),
    ('ubuntu_22', 'Ubuntu 22.04 LTS'),
    ('debian_10', 'Debian 10'),
    ('debian_11', 'Debian 11'),
    ('other', 'Other'),
]


class Server(models.Model):
    """Comprehensive server inventory"""
    # Basic Identification
    name = models.CharField(max_length=255, unique=True)
    serial_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    asset_tag = models.CharField(max_length=100, blank=True, null=True)
    
    # Network Information
    ip_address = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255, blank=True, null=True)
    mac_address = models.CharField(max_length=17, blank=True, null=True)
    
    # Location
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='servers')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True, related_name='servers')
    rack_position = models.PositiveIntegerField(blank=True, null=True, help_text="Starting U slot (1 = bottom of rack)")
    rack_units = models.PositiveIntegerField(default=1, help_text="Height in U")
    
    # Server Type & Status
    server_type = models.CharField(
        max_length=20,
        choices=[
            ('physical', 'Physical'),
            ('virtual', 'Virtual'),
            ('blade', 'Blade'),
            ('tower', 'Tower'),
        ],
        default='physical'
    )
    status = models.CharField(max_length=20, choices=SERVER_STATUS_CHOICES, default='active')
    environment = models.CharField(max_length=20, choices=SERVER_ENVIRONMENT_CHOICES, default='production')
    
    # Operating System
    os = models.CharField(max_length=100, help_text="e.g., Win 2019 Std, Rocky Linux 9, ESXi 7")
    os_version = models.CharField(max_length=100, blank=True, null=True)

    # Overview
    description = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., AD/DNS Primary")
    domain = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., LA.CONCENTRIX.COM")
    power_state = models.CharField(
        max_length=20,
        choices=[
            ('powered_on', 'Powered On'),
            ('powered_off', 'Powered Off'),
            ('unknown', 'Unknown'),
        ],
        default='unknown'
    )
    
    # Hardware Specifications
    cpu_model = models.CharField(max_length=255, blank=True, null=True)
    cpu_cores = models.IntegerField(blank=True, null=True)
    cpu_threads = models.IntegerField(blank=True, null=True)
    
    memory_gb = models.IntegerField(blank=True, null=True, help_text="Total RAM in GB")
    
    # Storage
    storage_total_gb = models.IntegerField(blank=True, null=True, help_text="Total storage in GB")
    storage_type = models.CharField(
        max_length=20,
        choices=[
            ('ssd', 'SSD'),
            ('hdd', 'HDD'),
            ('nvme', 'NVMe'),
            ('mixed', 'Mixed'),
        ],
        default='ssd'
    )
    storage_info = models.TextField(blank=True, null=True, help_text="Detailed storage configuration")
    
    # iDRAC Information (Dell servers)
    idrac_ip = models.GenericIPAddressField(blank=True, null=True)
    idrac_username = models.CharField(max_length=100, blank=True, null=True)
    idrac_password = models.CharField(max_length=255, blank=True, null=True, help_text="Store securely")
    
    # Power & Connectivity
    power_supply_count = models.IntegerField(default=1)
    network_interfaces = models.IntegerField(default=2)
    
    # Manufacturer & Model
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)

    # Procurement & Warranty
    warranty_vendor = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Dell, HP, Relutech")
    server_po = models.CharField(max_length=100, blank=True, null=True, help_text="Purchase order number")
    windows_license_po = models.CharField(max_length=100, blank=True, null=True, help_text="Windows license PO number")
    
    # Dates & Lifecycle
    purchase_date = models.DateField(blank=True, null=True)
    warranty_expiry = models.DateField(blank=True, null=True)
    last_maintenance = models.DateField(blank=True, null=True)
    decommission_date = models.DateField(blank=True, null=True)
    
    # Additional Info
    assigned_to = models.CharField(max_length=255, blank=True, null=True, help_text="Team or person")
    notes = models.TextField(blank=True, null=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Server'
        verbose_name_plural = 'Servers'
        indexes = [
            models.Index(fields=['status', 'environment']),
            models.Index(fields=['site', 'status']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.ip_address})"
    
    def is_production(self):
        """Check if server is in production"""
        return self.environment == 'production'
    
    def is_spare(self):
        """Check if server is spare"""
        return self.environment == 'spare' or self.status == 'spare'
    
    def get_hardware_summary(self):
        """Get summary of hardware specs"""
        parts = []
        if self.cpu_cores:
            parts.append(f"{self.cpu_cores}C" + (f"/{self.cpu_threads}T" if self.cpu_threads else ""))
        if self.memory_gb:
            parts.append(f"{self.memory_gb}GB RAM")
        if self.storage_total_gb:
            parts.append(f"{self.storage_total_gb}GB Storage")
        return ', '.join(parts) if parts else 'No hardware specs recorded'


class ServerMaintenance(models.Model):
    """Track server maintenance history"""
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='maintenance_records')
    
    maintenance_type = models.CharField(
        max_length=50,
        choices=[
            ('inspection', 'Inspection'),
            ('repair', 'Repair'),
            ('upgrade', 'Upgrade'),
            ('replacement', 'Replacement'),
            ('cleaning', 'Cleaning'),
            ('firmware_update', 'Firmware Update'),
            ('other', 'Other'),
        ]
    )
    
    description = models.TextField()
    performed_by = models.CharField(max_length=255)
    maintenance_date = models.DateField()
    
    next_maintenance_date = models.DateField(blank=True, null=True)
    parts_replaced = models.TextField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-maintenance_date']
        verbose_name = 'Server Maintenance'
        verbose_name_plural = 'Server Maintenance Records'
    
    def __str__(self):
        return f"{self.server.name} - {self.maintenance_type} ({self.maintenance_date})"


class ServerMonitoring(models.Model):
    """Track server monitoring and health status"""
    server = models.OneToOneField(Server, on_delete=models.CASCADE, related_name='monitoring')
    
    is_monitored = models.BooleanField(default=True)
    monitoring_tool = models.CharField(max_length=100, blank=True, null=True)
    
    # Health Status
    health_status = models.CharField(
        max_length=20,
        choices=[
            ('healthy', 'Healthy'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
            ('unknown', 'Unknown'),
        ],
        default='unknown'
    )
    
    # Key Metrics
    cpu_usage_percent = models.FloatField(default=0, help_text="Current CPU usage %")
    memory_usage_percent = models.FloatField(default=0, help_text="Current memory usage %")
    disk_usage_percent = models.FloatField(default=0, help_text="Current disk usage %")
    
    # Thresholds
    cpu_warning_threshold = models.FloatField(default=70)
    memory_warning_threshold = models.FloatField(default=80)
    disk_warning_threshold = models.FloatField(default=85)
    
    last_check_time = models.DateTimeField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Server Monitoring'
        verbose_name_plural = 'Server Monitoring'
    
    def __str__(self):
        return f"Monitoring: {self.server.name}"
    
    def get_health_color(self):
        """Return color for health status"""
        colors = {
            'healthy': 'success',
            'warning': 'warning',
            'critical': 'danger',
            'unknown': 'secondary',
        }
        return colors.get(self.health_status, 'secondary')
