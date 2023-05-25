import flet as ft


class WizardLoadingView(ft.UserControl):
    _progress_ring_ref: ft.Ref[ft.ProgressRing]

    def __init__(self, ref: ft.Ref["WizardLoadingView"]):
        super().__init__(ref=ref)
        self._progress_ring_ref = ft.Ref[ft.ProgressRing]()

    @property
    def value(self) -> float:
        return self._progress_ring_ref.current.value

    @value.setter
    def value(self, new_value: float):
        self._progress_ring_ref.current.value = new_value
        self.update()

    def build(self) -> ft.Control:
        return ft.ProgressRing(
            ref=self._progress_ring_ref,
            width=200,
            height=200,
            value=0,
        )
