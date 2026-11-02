"""Dashboard, product, stockist, pincode, and audit API tests."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.models import Product, Stockist, StockistPincode
from conftest import login_headers


def create_product_payload(**overrides):
    return {
        "name": "Vyanic Serum",
        "sku_code": "SERUM-001",
        "category": "Skin Care",
        "price": 249.50,
        "stock_quantity": 25,
        **overrides,
    }


def create_stockist_payload(**overrides):
    return {
        "name": "North Star Distribution",
        "contact_email": "north@example.com",
        "contact_phone": "+91 98765 43210",
        "city": "Delhi",
        **overrides,
    }


def seed_business_data(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        stockist = Stockist(
            name="Dashboard Stockist",
            contact_email="dashboard@example.com",
            contact_phone="9876543210",
            city="Pune",
        )
        session.add(stockist)
        session.flush()
        session.add_all(
            [
                Product(
                    name="Dashboard Product",
                    sku_code="DASH-001",
                    category="General",
                    price=Decimal("10.00"),
                    stock_quantity=4,
                ),
                StockistPincode(stockist_id=stockist.id, pincode="411001", state="Maharashtra"),
                StockistPincode(stockist_id=stockist.id, pincode="411002", state="Maharashtra"),
            ]
        )
        session.commit()


def test_dashboard_stats_use_sql_counts_and_latest_five_audits(api_client) -> None:
    client, session_factory, audit_collection = api_client
    seed_business_data(session_factory)
    start = datetime.now(timezone.utc)
    for index in range(6):
        audit_collection.seed(timestamp=start + timedelta(seconds=index))

    response = client.get("/dashboard/stats", headers=login_headers(client, "stockist"))

    assert response.status_code == 200
    assert response.json()["total_products"] == 1
    assert response.json()["total_stockists"] == 1
    assert response.json()["total_pincodes_assigned"] == 2
    activity = response.json()["recent_activity"]
    assert len(activity) == 5
    assert activity[0]["timestamp"] > activity[-1]["timestamp"]


def test_dashboard_stats_require_authentication(api_client) -> None:
    client, _, _ = api_client
    assert client.get("/dashboard/stats").status_code == 401


def test_admin_product_create_update_delete_write_audit_events(api_client) -> None:
    client, _, audit_collection = api_client
    headers = login_headers(client)

    created = client.post("/products", json=create_product_payload(), headers=headers)
    assert created.status_code == 201
    product_id = created.json()["id"]

    updated = client.put(
        f"/products/{product_id}",
        json=create_product_payload(name="Vyanic Serum Plus", stock_quantity=31),
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Vyanic Serum Plus"
    assert updated.json()["stock_quantity"] == 31

    deleted = client.delete(f"/products/{product_id}", headers=headers)
    assert deleted.status_code == 204
    assert deleted.content == b""

    assert [(event["action"], event["module"]) for event in audit_collection.documents] == [
        ("CREATE", "Product"),
        ("UPDATE", "Product"),
        ("DELETE", "Product"),
    ]
    assert all(event["user_id"] == 1 for event in audit_collection.documents)
    assert all(event["user_email"] == "admin@example.com" for event in audit_collection.documents)
    assert all(isinstance(event["details"], dict) for event in audit_collection.documents)
    assert all("timestamp" in event for event in audit_collection.documents)


def test_product_rejects_duplicate_sku_with_conflict(api_client) -> None:
    client, _, audit_collection = api_client
    headers = login_headers(client)
    assert client.post("/products", json=create_product_payload(), headers=headers).status_code == 201

    duplicate = client.post(
        "/products",
        json=create_product_payload(name="Different label", sku_code="serum-001"),
        headers=headers,
    )

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "A product with this SKU code already exists."
    assert len(audit_collection.documents) == 1


def test_product_pagination_search_and_category_filtering(api_client) -> None:
    client, session_factory, _ = api_client
    headers = login_headers(client, "stockist")
    with session_factory() as session:
        session.add_all(
            [
                Product(name="Amber Cream", sku_code="SKIN-001", category="Skin Care", price=10, stock_quantity=2),
                Product(name="Cedar Balm", sku_code="BODY-001", category="Body Care", price=11, stock_quantity=3),
                Product(name="Rose Serum", sku_code="SKIN-002", category="Skin Care", price=12, stock_quantity=4),
                Product(name="Sage Wash", sku_code="BODY-002", category="Body Care", price=13, stock_quantity=5),
            ]
        )
        session.commit()

    page = client.get("/products?page=2&limit=2", headers=headers)
    assert page.status_code == 200
    assert page.json()["total"] == 4
    assert page.json()["pages"] == 2
    assert [item["name"] for item in page.json()["items"]] == ["Rose Serum", "Sage Wash"]

    by_name = client.get("/products?search=rose", headers=headers)
    assert [item["sku_code"] for item in by_name.json()["items"]] == ["SKIN-002"]

    by_sku = client.get("/products?search=BODY-002", headers=headers)
    assert [item["name"] for item in by_sku.json()["items"]] == ["Sage Wash"]

    by_category = client.get("/products?category=skin%20care", headers=headers)
    assert [item["name"] for item in by_category.json()["items"]] == ["Amber Cream", "Rose Serum"]


def test_product_validates_fields_and_missing_update_returns_404(api_client) -> None:
    client, _, _ = api_client
    headers = login_headers(client)

    invalid = client.post(
        "/products",
        json=create_product_payload(price=-1, stock_quantity=-2),
        headers=headers,
    )
    assert invalid.status_code == 422

    missing = client.put(
        "/products/999",
        json=create_product_payload(),
        headers=headers,
    )
    assert missing.status_code == 404


def test_stockist_creation_and_pincode_assignment_are_audited(api_client) -> None:
    client, _, audit_collection = api_client
    headers = login_headers(client)

    created = client.post("/stockists", json=create_stockist_payload(), headers=headers)
    assert created.status_code == 201
    stockist_id = created.json()["id"]
    assert created.json()["contact_email"] == "north@example.com"
    assert audit_collection.documents[-1]["action"] == "CREATE"
    assert audit_collection.documents[-1]["module"] == "Stockist"

    assigned = client.post(
        f"/stockists/{stockist_id}/pincodes",
        json={"pincode": "110001", "state": "Delhi"},
        headers=headers,
    )
    assert assigned.status_code == 201
    assert assigned.json()["pincode"] == "110001"
    assert audit_collection.documents[-1]["module"] == "Pincode"

    listed_stockists = client.get("/stockists", headers=headers)
    listed_pincodes = client.get(f"/stockists/{stockist_id}/pincodes", headers=headers)
    assert listed_stockists.status_code == 200
    assert len(listed_stockists.json()) == 1
    assert listed_pincodes.status_code == 200
    assert [item["pincode"] for item in listed_pincodes.json()] == ["110001"]


def test_duplicate_pincode_returns_required_message(api_client) -> None:
    client, _, audit_collection = api_client
    headers = login_headers(client)
    first = client.post("/stockists", json=create_stockist_payload(), headers=headers)
    second = client.post(
        "/stockists",
        json=create_stockist_payload(
            name="South Star Distribution",
            contact_email="south@example.com",
            city="Chennai",
        ),
        headers=headers,
    )
    first_id = first.json()["id"]
    second_id = second.json()["id"]

    assigned = client.post(
        f"/stockists/{first_id}/pincodes",
        json={"pincode": "600001", "state": "Tamil Nadu"},
        headers=headers,
    )
    assert assigned.status_code == 201
    audit_count_before_duplicate = len(audit_collection.documents)

    duplicate = client.post(
        f"/stockists/{second_id}/pincodes",
        json={"pincode": "600001", "state": "Tamil Nadu"},
        headers=headers,
    )
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "This pincode is already assigned to another stockist."
    assert len(audit_collection.documents) == audit_count_before_duplicate


def test_stockist_and_pincode_validation(api_client) -> None:
    client, _, _ = api_client
    headers = login_headers(client)

    invalid_stockist = client.post(
        "/stockists",
        json=create_stockist_payload(contact_email="invalid", contact_phone="abc"),
        headers=headers,
    )
    assert invalid_stockist.status_code == 422

    created = client.post("/stockists", json=create_stockist_payload(), headers=headers)
    invalid_pincode = client.post(
        f"/stockists/{created.json()['id']}/pincodes",
        json={"pincode": "123", "state": "Delhi"},
        headers=headers,
    )
    assert invalid_pincode.status_code == 422


def test_stockist_role_can_read_but_cannot_write(api_client) -> None:
    client, _, audit_collection = api_client
    headers = login_headers(client, "stockist")

    assert client.get("/products", headers=headers).status_code == 200
    assert client.get("/stockists", headers=headers).status_code == 200
    assert client.post("/products", json=create_product_payload(), headers=headers).status_code == 403
    assert client.post("/stockists", json=create_stockist_payload(), headers=headers).status_code == 403

    admin_headers = login_headers(client)
    stockist = client.post(
        "/stockists",
        json=create_stockist_payload(),
        headers=admin_headers,
    )
    denied_assignment = client.post(
        f"/stockists/{stockist.json()['id']}/pincodes",
        json={"pincode": "110001", "state": "Delhi"},
        headers=headers,
    )
    assert denied_assignment.status_code == 403
    assert len(audit_collection.documents) == 1


def test_viewer_role_can_read_but_cannot_write(api_client) -> None:
    client, _, _ = api_client
    headers = login_headers(client, "viewer")

    assert client.get("/dashboard/stats", headers=headers).status_code == 200
    assert client.get("/products", headers=headers).status_code == 200
    assert client.get("/stockists", headers=headers).status_code == 200
    assert client.get("/audit-logs", headers=headers).status_code == 200
    assert client.post("/products", json=create_product_payload(), headers=headers).status_code == 403
    assert client.post("/stockists", json=create_stockist_payload(), headers=headers).status_code == 403


def test_all_business_endpoints_require_a_bearer_token(api_client) -> None:
    client, _, _ = api_client
    payload = create_product_payload()

    responses = [
        client.get("/products"),
        client.post("/products", json=payload),
        client.put("/products/1", json=payload),
        client.delete("/products/1"),
        client.get("/stockists"),
        client.post("/stockists", json=create_stockist_payload()),
        client.get("/stockists/1/pincodes"),
        client.post("/stockists/1/pincodes", json={"pincode": "110001", "state": "Delhi"}),
        client.get("/audit-logs"),
        client.get("/dashboard/stats"),
    ]

    assert all(response.status_code == 401 for response in responses)


def test_audit_write_failure_rolls_back_product_and_returns_service_error(api_client) -> None:
    client, session_factory, audit_collection = api_client
    headers = login_headers(client)
    audit_collection.fail_writes = True

    response = client.post("/products", json=create_product_payload(), headers=headers)

    assert response.status_code == 503
    assert "audit log could not be written" in response.json()["detail"]
    assert audit_collection.documents == []
    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(Product)) == 0


def test_product_audit_event_is_inserted_into_real_mongo(mongo_audit_client) -> None:
    client, _, collection = mongo_audit_client
    response = client.post(
        "/products",
        json=create_product_payload(),
        headers=login_headers(client),
    )

    assert response.status_code == 201
    event = collection.find_one({"module": "Product", "action": "CREATE"})
    assert event is not None
    assert event["user_id"] == 1
    assert event["user_email"] == "admin@example.com"
    assert isinstance(event["details"], dict)
    assert event["timestamp"].tzinfo is not None


def test_product_price_update_is_audited_and_returned_with_updated_values(mongo_audit_client) -> None:
    client, _, collection = mongo_audit_client
    headers = login_headers(client)
    created = client.post(
        "/products",
        json=create_product_payload(price=2499),
        headers=headers,
    )
    assert created.status_code == 201

    updated = client.put(
        f"/products/{created.json()['id']}",
        json=create_product_payload(price=2599, stock_quantity=38),
        headers=headers,
    )
    assert updated.status_code == 200
    assert float(updated.json()["price"]) == 2599.0

    event = collection.find_one({"module": "Product", "action": "UPDATE"})
    assert event is not None
    assert event["details"]["before"]["price"] == "2499.00"
    assert event["details"]["after"]["price"] == "2599.00"
    assert event["details"]["after"]["stock_quantity"] == 38

    audit_response = client.get("/audit-logs", headers=headers)
    assert audit_response.status_code == 200
    visible_update = next(
        entry for entry in audit_response.json() if entry["id"] == str(event["_id"])
    )
    assert visible_update["action"] == "UPDATE"
    assert visible_update["details"]["after"]["price"] == "2599.00"


def test_audit_logs_api_requires_auth_and_returns_latest_fifty(api_client) -> None:
    client, _, audit_collection = api_client
    now = datetime.now(timezone.utc)
    for index in range(55):
        audit_collection.seed(timestamp=now + timedelta(seconds=index))

    assert client.get("/audit-logs").status_code == 401
    response = client.get("/audit-logs", headers=login_headers(client, "stockist"))

    assert response.status_code == 200
    assert len(response.json()) == 50
    assert response.json()[0]["timestamp"] > response.json()[-1]["timestamp"]
