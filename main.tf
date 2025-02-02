# Specify the Terraform provider for Google Cloud
provider "google" {
  credentials = file(var.GOOGLE_APPLICATION_CREDENTIALS)
  project     = var.GOOGLE_CLOUD_PROJECT
  region      = "europe-west2"
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
      apt-get install -y postgresql postgresql-contrib
      systemctl enable docker
      systemctl start docker
      systemctl enable postgresql
      systemctl start postgresql

      # Configure PostgreSQL
      sudo -u postgres psql -c "CREATE USER ${var.POSTGRES_USER} WITH PASSWORD '${var.POSTGRES_PASSWORD}';"
      sudo -u postgres psql -c "CREATE DATABASE ${var.POSTGRES_DB};"
      sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${var.POSTGRES_DB} TO ${var.POSTGRES_USER};"

      # Pull the frontend and backend images
      echo "Pulling frontend image..." > /var/log/startup.log
      docker pull ${var.frontend_image} >> /var/log/startup.log 2>&1
      echo "Pulling backend image..." >> /var/log/startup.log
      docker pull ${var.backend_image} >> /var/log/startup.log 2>&1

      # Start frontend and backend containers, ensuring backend connects to PostgreSQL
      echo "Starting frontend container..." >> /var/log/startup.log
      docker run -d -p 3000:3000 ${var.frontend_image} >> /var/log/startup.log 2>&1
      
      echo "Starting backend container with PostgreSQL connection..." >> /var/log/startup.log
      docker run -d -p 8000:8000 \
        -e DB_HOST=${var.POSTGRES_HOST} \
        -e DB_PORT=${var.POSTGRES_PORT} \
        -e DB_NAME=${var.POSTGRES_DB} \
        -e DB_USER=${var.POSTGRES_USER} \
        -e DB_PASSWORD=${var.POSTGRES_PASSWORD} \
        ${var.backend_image} >> /var/log/startup.log 2>&1
    EOT
  }
}

# Create a firewall rule to allow HTTP/HTTPS traffic
resource "google_compute_firewall" "default" {
  name    = "default-allow-http-https"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8000", "3000", "5432"]  # Allowing 8000 and 3000 for frontend and backend
  }

  source_ranges = ["0.0.0.0/0"]  # Allows incoming traffic from any IP address.

  target_tags = ["http-server", "https-server"]
}

# Output the external IP address of the VM
output "instance_external_ip" {
  value = google_compute_instance.default.network_interface[0].access_config[0].nat_ip
}