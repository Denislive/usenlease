# File: variables.tf

# Google Cloud Credentials
variable "GOOGLE_APPLICATION_CREDENTIALS" {
  description = "Path to Google Cloud application credentials"
  type        = string
}

variable "GOOGLE_CLOUD_PROJECT" {
  description = "Google Cloud project ID"
  type        = string
}

variable "GOOGLE_CLOUD_ZONE" {
  description = "Google Cloud zone"
  type        = string
}

# Docker images for frontend and backend
variable "frontend_image" {
  description = "Docker image for the frontend service"
  type        = string
}

variable "backend_image" {
  description = "Docker image for the backend service"
  type        = string
}

# PostgreSQL Database Configuration
variable "POSTGRES_USER" {
  description = "Username for the PostgreSQL database"
  type        = string
}

variable "POSTGRES_PASSWORD" {
  description = "Password for the PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "POSTGRES_DB" {
  description = "Name of the PostgreSQL database"
  type        = string
}

variable "DB_HOST" {
  description = "Hostname for the PostgreSQL database"
  type        = string
  default     = "usenlease-db"
}

variable "DB_PORT" {
  description = "Port for the PostgreSQL database"
  type        = string
  default     = "5432"
}
