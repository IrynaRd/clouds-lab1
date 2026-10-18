variable "db_user" {
  description = "username db"
  type        = string
}

variable "db_password" {
  description = "db_password"
  type        = string
  sensitive   = true
}

variable "db_rootpassword" {
  description = "db_rootpassword"
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "JWT secret key"
  type        = string
  sensitive   = true
}

variable "alert_email" {
  description = "alert email"
  type        = string
  sensitive   = true
}