resource "google_project_service" "monitoring" {
  service            = "monitoring.googleapis.com"
  disable_on_destroy = false
}

resource "google_monitoring_notification_channel" "email" {
  project      = var.project_id
  display_name = "Jonatan email"
  type         = "email"
  labels = {
    email_address = "jonatan.wulcan@gmail.com"
  }
  depends_on = [google_project_service.monitoring]
}

resource "google_billing_budget" "monthly" {
  billing_account = "0154A5-226FA3-331C47"
  display_name    = "Monthly 100 SEK"

  budget_filter {
    projects = ["projects/${data.google_project.default.number}"]
  }

  amount {
    specified_amount {
      currency_code = "SEK"
      units         = 100
    }
  }

  threshold_rules {
    threshold_percent = 0.5
  }
  threshold_rules {
    threshold_percent = 0.9
  }
  threshold_rules {
    threshold_percent = 1.0
  }

  all_updates_rule {
    monitoring_notification_channels = [
      google_monitoring_notification_channel.email.id,
    ]
    disable_default_iam_recipients = true
  }
}

data "google_project" "default" {
  project_id = var.project_id
}
