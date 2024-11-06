provider "google" {
  credentials = file("/home/nelson-ngumo/Documents/burnished-ether-439413-s1-579bee90267c.json")
  project     = "usenlease-docker-vm"
  region      = "us-central1"
  zone        = "us-central1-a"
}

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
      // The VM will be assigned an ephemeral external IP
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
      docker pull ngumonelson123/frontend-image:latest
      docker pull ngumonelson123/backend-image:latest
      # Running the frontend container on port 8000
      docker run -d -p 8000:8000 ngumonelson123/frontend-image:latest
      # Running the backend container on port 3000
      docker run -d -p 3000:3000 ngumonelson123/backend-image:latest
    EOT
  }
}

resource "google_compute_firewall" "default" {
  name    = "default-allow-http-https"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8000", "3000"]  # Allowing 8000 and 3000 for frontend and backend
  }

  target_tags = ["http-server", "https-server"]
}
