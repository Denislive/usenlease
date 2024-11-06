# Specify the Terraform provider for Google Cloud
provider "google" {
  credentials = file(var.GOOGLE_APPLICATION_CREDENTIALS)
  project     = var.GOOGLE_CLOUD_PROJECT
  region      = "us-central1"
  zone        = var.GOOGLE_CLOUD_ZONE
}

# Create the Google Compute instance
resource "google_compute_instance" "default" {
  name         = "usenlease-docker-vm"
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
      docker pull ${var.frontend_image}
      docker pull ${var.backend_image}
      docker run -d -p 8000:8000 ${var.frontend_image}
      docker run -d -p 3000:3000 ${var.backend_image}
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
