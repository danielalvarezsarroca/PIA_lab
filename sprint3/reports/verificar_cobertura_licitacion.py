from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKLIST_PATH = Path(__file__).with_name("licitacion_coverage_checklist.json")

REQUIRED_REQUIREMENT_IDS = {"i", "ii", "iii", "iv", "v"}
REQUIRED_TOP_LEVEL = {
    "generated_at",
    "purpose",
    "project_context",
    "tender_questions",
    "requirements",
    "budget_eur",
}
REQUIRED_TENDER_QUESTIONS = {
    "answerable_now",
    "remaining_work",
    "timeline",
    "organization",
    "budget_summary",
}
REQUIRED_REQUIREMENT_FIELDS = {
    "id",
    "requirement",
    "status",
    "status_label",
    "evidence",
    "presentation_message",
    "remaining_work",
    "capacity_to_finish",
}
REQUIRED_BUDGET_FIELDS = {
    "currency",
    "prototype_executed_cost",
    "continuity_total",
    "total_program",
    "work_packages",
    "assumptions",
}
ALLOWED_STATUSES = {"implemented", "partial", "planned"}


def _is_present(value: Any) -> bool:
    return value not in (None, "", [], {})


def _load_checklist() -> dict[str, Any]:
    if not CHECKLIST_PATH.exists():
        raise SystemExit(f"No existe el checklist: {CHECKLIST_PATH}")
    return json.loads(CHECKLIST_PATH.read_text(encoding="utf-8"))


def _validate_top_level(data: dict[str, Any], errors: list[str]) -> None:
    for field in sorted(REQUIRED_TOP_LEVEL):
        if not _is_present(data.get(field)):
            errors.append(f"Falta campo principal: {field}")


def _validate_tender_questions(data: dict[str, Any], errors: list[str]) -> None:
    questions = data.get("tender_questions", {})
    for field in sorted(REQUIRED_TENDER_QUESTIONS):
        if not _is_present(questions.get(field)):
            errors.append(f"Falta respuesta a pregunta de licitacion: {field}")


def _validate_requirements(data: dict[str, Any], errors: list[str]) -> Counter:
    requirements = data.get("requirements", [])
    if not isinstance(requirements, list):
        errors.append("requirements debe ser una lista")
        return Counter()

    ids = {str(item.get("id")) for item in requirements if isinstance(item, dict)}
    missing_ids = REQUIRED_REQUIREMENT_IDS - ids
    extra_ids = ids - REQUIRED_REQUIREMENT_IDS
    if missing_ids:
        errors.append(f"Faltan apartados de licitacion: {sorted(missing_ids)}")
    if extra_ids:
        errors.append(f"Apartados no esperados: {sorted(extra_ids)}")

    status_counter: Counter = Counter()
    for item in requirements:
        if not isinstance(item, dict):
            errors.append("Cada requisito debe ser un objeto JSON")
            continue

        req_id = item.get("id", "<sin id>")
        for field in sorted(REQUIRED_REQUIREMENT_FIELDS):
            if not _is_present(item.get(field)):
                errors.append(f"Requisito {req_id}: falta campo {field}")

        status = item.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"Requisito {req_id}: estado no valido {status!r}")
        else:
            status_counter[status] += 1

        evidence = item.get("evidence", [])
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"Requisito {req_id}: evidencia vacia")
            continue

        for evidence_item in evidence:
            if not isinstance(evidence_item, dict):
                errors.append(f"Requisito {req_id}: evidencia debe ser objeto")
                continue
            path = evidence_item.get("path")
            why = evidence_item.get("why")
            if not path:
                errors.append(f"Requisito {req_id}: evidencia sin path")
                continue
            if not why:
                errors.append(f"Requisito {req_id}: evidencia sin explicacion")
            if not (REPO_ROOT / path).exists():
                errors.append(f"Requisito {req_id}: no existe evidencia {path}")

    return status_counter


def _validate_budget(data: dict[str, Any], errors: list[str]) -> None:
    budget = data.get("budget_eur", {})
    for field in sorted(REQUIRED_BUDGET_FIELDS):
        if not _is_present(budget.get(field)):
            errors.append(f"Falta campo de presupuesto: {field}")

    if budget.get("currency") != "EUR":
        errors.append("Presupuesto currency: debe ser EUR")

    for field in ("prototype_executed_cost", "continuity_total", "total_program"):
        value = budget.get(field)
        if not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"Presupuesto {field}: debe ser numerico y positivo")

    assumptions = budget.get("assumptions")
    if isinstance(assumptions, list) and len(assumptions) < 2:
        errors.append("Presupuesto: assumptions debe incluir al menos dos supuestos")

    work_packages = budget.get("work_packages", [])
    package_total = 0.0
    if not isinstance(work_packages, list) or not work_packages:
        errors.append("Presupuesto work_packages: debe ser una lista no vacia")
    else:
        for index, package in enumerate(work_packages, start=1):
            if not isinstance(package, dict):
                errors.append(f"Presupuesto work_package {index}: debe ser objeto")
                continue
            for field in ("wp", "block", "amount_eur"):
                if not _is_present(package.get(field)):
                    errors.append(f"Presupuesto work_package {index}: falta campo {field}")
            amount = package.get("amount_eur")
            if not isinstance(amount, (int, float)) or amount <= 0:
                errors.append(f"Presupuesto work_package {index}: amount_eur debe ser positivo")
            else:
                package_total += float(amount)

    continuity = budget.get("continuity_total")
    prototype = budget.get("prototype_executed_cost")
    total_program = budget.get("total_program")
    if (
        isinstance(continuity, (int, float))
        and package_total
        and abs(package_total - float(continuity)) > 0.01
    ):
        errors.append("Presupuesto: suma de work_packages no coincide con continuity_total")
    if all(isinstance(value, (int, float)) for value in (prototype, continuity, total_program)):
        expected_total = float(prototype) + float(continuity)
        if abs(expected_total - float(total_program)) > 0.01:
            errors.append(
                "Presupuesto: prototype_executed_cost + continuity_total no coincide con total_program"
            )


def main() -> None:
    data = _load_checklist()
    errors: list[str] = []

    _validate_top_level(data, errors)
    _validate_tender_questions(data, errors)
    status_counter = _validate_requirements(data, errors)
    _validate_budget(data, errors)

    if errors:
        print("Cobertura de licitacion NO verificada:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    budget = data["budget_eur"]
    print("Cobertura de licitacion verificada")
    print(
        "Requisitos i-v: "
        f"{sum(status_counter.values())} "
        f"({status_counter['implemented']} cubiertos, "
        f"{status_counter['partial']} parciales, "
        f"{status_counter['planned']} planificados)"
    )
    print(
        "Preguntas de empresa: respuesta actual, faena restante, plan, organizacion y presupuesto cubiertos"
    )
    print(f"Presupuesto continuidad: {budget['continuity_total']} {budget['currency']}")
    print(f"Programa completo: {budget['total_program']} {budget['currency']}")


if __name__ == "__main__":
    main()
