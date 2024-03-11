resource "google_artifact_registry_repository" "esports-earnings-repo" {
  location = var.REGION
  repository_id = "esports-earnings-repo"
  description = "Docker repository"
  format = "docker"
}