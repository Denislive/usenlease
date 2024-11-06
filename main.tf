# Specify the Terraform provider for Google Cloud
provider "google" {
  credentials = file(var.GOOGLE_APPLICATION_CREDENTIALS)
  project     = "usenlease-docker-vm"
  region      = "us-central1"
  zone        = "us-central1-a"
}

# Declare the missing variables for frontend and backend image
variable "frontend_image" {
  description = "Docker image for the frontend"
  type        = string
}

variable "backend_image" {
  description = "Docker image for the backend"
  type        = string
}

# Create the Google Compute instance
resource "google_compute_instance" "default" {
  name         = "usenlease-docker-vm"
  machine_type = "e2-medium"
  zone         = "us-central1-a"
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11-bullseye-v20230404"
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
      # Running the frontend container on port 8000
      docker run -d -p 8000:8000 ${var.frontend_image}
      # Running the backend container on port 3000
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

  target_tags = ["http-server", "https-server"]
}
