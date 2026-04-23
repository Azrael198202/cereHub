from core.contracts.artifact import ArtifactModel


def register_artifacts(artifacts: list[ArtifactModel]) -> list[str]:
    return [artifact.id for artifact in artifacts]
