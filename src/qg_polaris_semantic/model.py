"""Open Semantic Interchange style objects used by the examples."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class OsiMeasure:
    name: str
    expr: str
    agg: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "expr": self.expr,
            "agg": self.agg,
            "description": self.description,
        }


@dataclass(frozen=True)
class OsiDimension:
    name: str
    type: str
    expr: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "expr": self.expr,
            "description": self.description,
        }


@dataclass(frozen=True)
class OsiMetric:
    name: str
    type: str
    measure_name: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "type_params": {
                "measure": {
                    "name": self.measure_name,
                },
            },
        }


@dataclass(frozen=True)
class OsiJoin:
    name: str
    relationship: str
    left_on: str
    right_on: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "relationship": self.relationship,
            "left_on": self.left_on,
            "right_on": self.right_on,
        }


@dataclass(frozen=True)
class OsiSemanticModel:
    name: str
    description: str
    catalog: str
    namespace: str
    table: str
    owner: str
    landing_page: str
    data_url: str
    dimensions: list[OsiDimension] = field(default_factory=list)
    measures: list[OsiMeasure] = field(default_factory=list)
    metrics: list[OsiMetric] = field(default_factory=list)
    joins: list[OsiJoin] = field(default_factory=list)

    @property
    def iceberg_identifier(self) -> str:
        return f"{self.catalog}.{self.namespace}.{self.table}"

    def to_osi_dict(self) -> dict[str, Any]:
        return {
            "semantic_models": [
                {
                    "name": self.name,
                    "description": self.description,
                    "model": self.table,
                    "entities": [
                        {
                            "name": "order",
                            "type": "primary",
                            "expr": "order_id",
                        },
                        {
                            "name": "customer",
                            "type": "foreign",
                            "expr": "customer_id",
                        },
                    ],
                    "dimensions": [dimension.to_dict() for dimension in self.dimensions],
                    "measures": [measure.to_dict() for measure in self.measures],
                    "metrics": [metric.to_dict() for metric in self.metrics],
                    "joins": [join.to_dict() for join in self.joins],
                }
            ]
        }


def example_revenue_model() -> OsiSemanticModel:
    """Return the canonical model used across all examples."""

    return OsiSemanticModel(
        name="revenue_semantics",
        description=(
            "Governed revenue semantics for orders, customers, and AI-safe "
            "agent discovery."
        ),
        catalog="lakehouse",
        namespace="analytics",
        table="orders",
        owner="did:example:querygraph-ai-navigator",
        landing_page="https://querygraph.ai/examples/revenue-semantics",
        data_url="s3://warehouse/analytics/orders/",
        dimensions=[
            OsiDimension(
                name="order_date",
                type="time",
                expr="orders.order_date",
                description="Date when the order was accepted.",
            ),
            OsiDimension(
                name="customer_region",
                type="categorical",
                expr="customers.region",
                description="Commercial region assigned to the customer.",
            ),
            OsiDimension(
                name="product_category",
                type="categorical",
                expr="products.category",
                description="Product category used for revenue reporting.",
            ),
        ],
        measures=[
            OsiMeasure(
                name="revenue",
                expr="orders.order_total",
                agg="sum",
                description="Gross order revenue before refunds.",
            ),
            OsiMeasure(
                name="orders",
                expr="orders.order_id",
                agg="count_distinct",
                description="Number of distinct orders.",
            ),
        ],
        metrics=[
            OsiMetric(
                name="total_revenue",
                type="simple",
                measure_name="revenue",
                description="Total gross order revenue.",
            ),
            OsiMetric(
                name="order_count",
                type="simple",
                measure_name="orders",
                description="Count of distinct orders.",
            ),
        ],
        joins=[
            OsiJoin(
                name="customers",
                relationship="many_to_one",
                left_on="orders.customer_id",
                right_on="customers.id",
            ),
            OsiJoin(
                name="products",
                relationship="many_to_one",
                left_on="orders.product_id",
                right_on="products.id",
            ),
        ],
    )

