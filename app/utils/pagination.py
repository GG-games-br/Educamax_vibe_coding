import math

class Pagination:
    """
    Utilitário de paginação reutilizável para listagens do sistema.
    Calcula páginas, fatias de itens e fornece controles de navegação.
    """
    def __init__(self, page, per_page, total_count, items):
        self.page = max(1, int(page))
        self.per_page = max(1, int(per_page))
        self.total_count = total_count
        self.items = items
        self.total_pages = max(1, math.ceil(total_count / self.per_page))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.total_pages

    @property
    def prev_num(self):
        return self.page - 1 if self.has_prev else None

    @property
    def next_num(self):
        return self.page + 1 if self.has_next else None

    def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
        """Gera a sequência de números de página para os links no template."""
        last = 0
        for num in range(1, self.total_pages + 1):
            if (
                num <= left_edge
                or (self.page - left_current <= num <= self.page + right_current)
                or num > self.total_pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num
