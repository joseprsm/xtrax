from xtrax.data import Dataset, Users, Items

from .base import BaseTransformer
from .context import ContextPipeline
from .transform import FeatureTransformer


class FeatureExtractor(BaseTransformer):
    def __init__(self, schema: dict, users: str, items: str, header: list[str]):
        self._users = users
        self._items = items

        self._user_transformer = FeatureTransformer(schema["user"])
        self._item_transformer = FeatureTransformer(schema["item"])

        transformers = self._get_transformers(schema, header)
        super().__init__(transformers=transformers, remainder="passthrough")

    def fit(self, X):
        def fit_transformer(inputs: Dataset, transformer: FeatureTransformer):
            input_attr: str = getattr(self, f"_{inputs.__name__.lower()}")
            x = inputs.load(input_attr, schema=self._schema)
            transformer.fit(x)

        fit_transformer(Users)
        fit_transformer(Items)

        X = self._user_transformer.encode(X)
        X = self._item_transformer.encode(X)

        super().fit(X)

    def _get_transformers(self, schema: dict, header: list[str]):
        context_indices = self._get_context_indices(schema, header)
        return [
            (
                ContextPipeline.__name__,
                ContextPipeline(schema),
                context_indices,
            )
        ]

    def _get_context_indices(cls, schema: dict, header: list[str]):
        raise NotImplementedError
