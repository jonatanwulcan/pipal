resource "google_project_service" "firebase" {
  service            = "firebase.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "firebase_hosting" {
  service            = "firebasehosting.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "identity_toolkit" {
  service            = "identitytoolkit.googleapis.com"
  disable_on_destroy = false
}

resource "google_firebase_project" "default" {
  provider = google-beta
  project  = var.project_id

  depends_on = [google_project_service.firebase]
}

resource "google_firebase_hosting_site" "default" {
  provider = google-beta
  project  = var.project_id
  site_id  = var.project_id

  depends_on = [
    google_firebase_project.default,
    google_project_service.firebase_hosting,
  ]
}

resource "google_firebase_web_app" "default" {
  provider     = google-beta
  project      = var.project_id
  display_name = "Pipal PWA"

  depends_on = [google_firebase_project.default]
}

data "google_firebase_web_app_config" "default" {
  provider   = google-beta
  web_app_id = google_firebase_web_app.default.app_id
}

output "hosting_url" {
  value = google_firebase_hosting_site.default.default_url
}

output "firebase_config" {
  value = {
    api_key            = data.google_firebase_web_app_config.default.api_key
    auth_domain        = data.google_firebase_web_app_config.default.auth_domain
    project_id         = var.project_id
    app_id             = google_firebase_web_app.default.app_id
    messaging_sender_id = data.google_firebase_web_app_config.default.messaging_sender_id
  }
}
