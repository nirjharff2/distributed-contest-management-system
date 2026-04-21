class NavigationMixin:
    def _show_page(self, key: str):
        if self._active_page:
            self._pages[self._active_page].pack_forget()
            self._sidebar_items[self._active_page].deselect()
        self._pages[key].pack(fill="both", expand=True)
        self._sidebar_items[key].select()
        self._active_page = key
