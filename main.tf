# Specify the Terraform provider for Google Cloud
provider "google" {
  credentials = file(var.GOOGLE_APPLICATION_CREDENTIALS)
  project     = var.GOOGLE_CLOUD_PROJECT
  region      = "us-central1"
  zone        = var.GOOGLE_CLOUD_ZONE
}

# Create the Google Compute instance
resource "google_compute_instance" "default" {
  name         = "usenlease-website"
  machine_type = "e2-medium"
  zone         = var.GOOGLE_CLOUD_ZONE
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {
      # The VM will be assigned an ephemeral external IP
    }
  }

  tags = ["http-server", "https-server"]

  metadata = {
    startup-script = <<-EOT
      #!/bin/bash
      apt-get update
      apt-get install -y docker.io
      systemctl enable docker
      systemctl start docker

      echo "Pulling frontend image..." > /var/log/startup.log
      docker pull ${var.frontend_image} >> /var/log/startup.log 2>&1
      echo "Pulling backend image..." >> /var/log/startup.log
      docker pull ${var.backend_image} >> /var/log/startup.log 2>&1

      echo "Starting frontend container..." >> /var/log/startup.log
      docker run -d -p 3000:3000 ${var.frontend_image} >> /var/log/startup.log 2>&1
      echo "Starting backend container..." >> /var/log/startup.log
      docker run -d -p 8000:8000 ${var.backend_image} >> /var/log/startup.log 2>&1
    EOT
  }
}

# Create a firewall rule to allow HTTP/HTTPS traffic
resource "google_compute_firewall" "default" {
  name    = "default-allow-http-https"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8000", "3000"]  # Allowing 8000 and 3000 for frontend and backend
  }

  source_ranges = ["0.0.0.0/0"]  # Allows incoming traffic from any IP address.

  target_tags = ["http-server", "https-server"]
}

# Output the external IP address of the VM
output "instance_external_ip" {
  value = google_compute_instance.default.network_interface[0].access_config[0].nat_ip
}
