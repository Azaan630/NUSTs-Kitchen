import flet as ft
import asyncio
import httpx
import os
import logging
from datetime import date, datetime
import mock_data
from flet_charts import (
    BarChart, BarChartGroup, BarChartRod, BarChartRodStackItem,
    PieChart, PieChartSection,
    LineChart, LineChartData, LineChartDataPoint,
    ChartCirclePoint,
    ChartAxis, ChartAxisLabel,
)

logging.basicConfig(level=logging.ERROR, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("admin")

BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")


async def _req(method, endpoint, params=None, json_data=None):
    async with httpx.AsyncClient() as client:
        try:
            url = f"{BASE_URL}{endpoint}"
            kw = dict(params=params, timeout=10.0)
            logger.error("REQ %s %s params=%s body=%s", method, url, params, json_data)
            if method == "GET":    r = await client.get(url, **kw)
            elif method == "POST":  r = await client.post(url, json=json_data, **kw)
            elif method == "PATCH": r = await client.patch(url, json=json_data, **kw)
            elif method == "DELETE":r = await client.delete(url, **kw)
            else: return {"error": "bad method"}
            r.raise_for_status()
            return r.json() if r.status_code != 204 else {}
        except httpx.HTTPStatusError as e:
            try: d = e.response.json().get("detail", e.response.text)
            except Exception: d = e.response.text
            msg = f"({e.response.status_code}) {d}"
            logger.error("REQ ERR %s %s -> %s", method, url, msg)
            return {"error": msg}
        except Exception as ex:
            logger.error("REQ EXC %s %s -> %s", method, url, ex)
            return {"error": str(ex)}


# ── API helpers ─────────────────────────────────────────────────

def _api(table):
    return {
        "students": {
            "all":   lambda e: _req("GET", "/admin/students/all", {"email": e}),
            "register": lambda e,d: _req("POST", "/admin/students/register", {"email": e}, d),
            "update": lambda e,i,d: _req("PATCH", f"/admin/students/update/{i}", {"email": e}, d),
            "delete": lambda e,i: _req("DELETE", f"/admin/students/delete/{i}", {"email": e}),
        },
        "staff": {
            "all":   lambda e: _req("GET", "/admin/staff/all", {"email": e}),
            "register": lambda e,d: _req("POST", "/admin/staff/register", {"email": e}, d),
            "update": lambda e,i,d: _req("PATCH", f"/admin/staff/update/{i}", {"email": e}, d),
            "delete": lambda e,i: _req("DELETE", f"/admin/staff/delete/{i}", {"email": e}),
        },
        "food": {
            "all":   lambda e: _req("GET", "/admin/food-items/all", {"email": e}),
            "create": lambda e,d: _req("POST", "/admin/food-items/create", {"email": e}, d),
            "update": lambda e,i,d: _req("PATCH", f"/admin/food-items/update/{i}", {"email": e}, d),
            "delete": lambda e,i: _req("DELETE", f"/admin/food-items/delete/{i}", {"email": e}),
            "search": lambda e,q: _req("GET", "/admin/food/search", {"email": e, "q": q}),
        },
        "ingredients": {
            "all":   lambda e: _req("GET", "/analytics/ingredients", {"email": e}),
            "create": lambda e,d: _req("POST", "/admin/ingredients/create", {"email": e}, d),
            "update": lambda e,i,d: _req("PATCH", f"/admin/ingredients/update/{i}", {"email": e}, d),
            "delete": lambda e,i: _req("DELETE", f"/admin/ingredients/delete/{i}", {"email": e}),
        },
        "mess_off": {
            "history": lambda e: _req("GET", "/student/mess-off/history", {"email": e}),
            "approve": lambda e,i: _req("POST", f"/admin/mess-off/approve/{i}", {"email": e}),
            "reject":  lambda e,i: _req("DELETE", f"/student/mess-off/cancel/{i}", {"email": e}),
        },
        "bills": {
            "all":      lambda e: _req("GET", "/admin/bills/all", {"email": e}),
            "summary":  lambda e: _req("GET", "/admin/monthly-billing-summary", {"email": e}),
            "create":   lambda e,d: _req("POST", "/admin/bills/create", {"email": e}, d),
            "export":   lambda e: _req("GET", "/admin/bills/export-csv", {"email": e}),
            "generate": lambda e,a: _req("POST", "/admin/bills/generate-monthly", {"email": e, "amount": a}),
            "update":   lambda e,i,d: _req("PATCH", f"/admin/bills/update/{i}", {"email": e}, d),
            "pay":      lambda e,i,a,m: _req("POST", f"/admin/bills/pay/{i}", {"email": e, "amount": a, "method": m}),
        },
        "menu": {
            "weekly": lambda e: _req("GET", "/menu/weekly", {"email": e}),
            "add":    lambda e,i,d,t: _req("POST", f"/admin/menu-schedule/{i}/{d}/{t}", {"email": e}),
            "delete": lambda e,i,s: _req("DELETE", f"/admin/menu-schedule/{i}/{s}", {"email": e}),
        },
        "registration": {
            "list":    lambda e,s: _req("GET", "/admin/registration-requests", {"email": e, "status": s}),
            "approve": lambda e,i,d: _req("POST", f"/admin/registration-requests/{i}/approve", {"email": e}, d),
            "reject":  lambda e,i: _req("POST", f"/admin/registration-requests/{i}/reject", {"email": e}),
        },
        "poll": {
            "start":   lambda e,d: _req("POST", "/admin/poll/start", {"email": e}, d),
            "results": lambda e: _req("GET", "/admin/poll/results", {"email": e}),
            "end":     lambda e: _req("POST", "/admin/poll/end", {"email": e}),
            "active":  lambda e: _req("GET", "/poll/active", {"email": e}),
        },
        "analytics": {
            "ratings":   lambda e: _req("GET", "/menu/ratings-summary", {"email": e}),
            "low_stock": lambda e: _req("GET", "/analytics/ingredients/low-stock", {"email": e}),
            "food_costs": lambda e: _req("GET", "/admin/food/costs", {"email": e}),
            "billing":  lambda e: _req("GET", "/admin/monthly-billing-summary", {"email": e}),
        },
        "stats": {
            "dashboard": lambda e: _req("GET", "/admin/dashboard/stats", {"email": e}),
            "activity":  lambda e: _req("GET", "/admin/activity/feed", {"email": e}),
        },
        "students_csv": lambda e: _req("GET", "/admin/students/export-csv", {"email": e}),
    }[table]


def _ensure_list(data):
    if isinstance(data, dict) and "error" in data:
        logger.warning("_ensure_list swallowed error: %s", data["error"])
    return data if isinstance(data, list) else []


class AdminPage:
    TABS = [
        ("Dashboard", ft.Icons.DASHBOARD_ROUNDED),
        ("Students",  ft.Icons.PEOPLE_ROUNDED),
        ("Staff",     ft.Icons.BADGE_ROUNDED),
        ("Food Items",ft.Icons.FASTFOOD_ROUNDED),
        ("Ingredients",ft.Icons.CATEGORY_ROUNDED),
        ("Mess Off",  ft.Icons.EVENT_BUSY_ROUNDED),
        ("Bills",     ft.Icons.RECEIPT_LONG_ROUNDED),
        ("Menu",      ft.Icons.RESTAURANT_MENU_ROUNDED),
        ("Polls",     ft.Icons.POLL_ROUNDED),
        ("Requests",  ft.Icons.PERSON_ADD_ALT_1_ROUNDED),
    ]

    def __init__(self, page, user_data, theme):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.email = user_data.get("Email", "")
        self.is_guest = theme.get("is_guest", False)
        self.tab_idx = {"v": 0}
        self.content = ft.Container(expand=True,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT))
        self.content.content = self._loading()
        self.proxy_rows = {}

    # ── helpers ─────────────────────────────────────────────────

    def _clr(self, key, fallback=None):
        return self.theme.get(key, fallback)

    def _loading(self, msg="Loading\u2026"):
        return ft.Container(
            ft.Column([
                ft.ProgressRing(width=32, height=32, stroke_width=3, color=self._clr("accent")),
                ft.Text(msg, size=13, color=self._clr("sub"), font_family="DM Sans"),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
            alignment=ft.Alignment(0, 0), expand=True,
        )

    def _snack(self, msg, ok=True):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="#FFF"),
            bgcolor=self._clr("success") if ok else self._clr("danger"),
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _run(self, coro):
        task = asyncio.create_task(coro)
        task.add_done_callback(lambda t: self._snack(str(t.exception()), False) if t.exception() else None)
        return task

    def _remove_overlay(self):
        o = getattr(self, '_active_overlay', None)
        if o and o in self.page.controls:
            self.page.remove(o)
        self._active_overlay = None
        if o:
            self.page.update()

    def _confirm(self, title, msg, on_delete):
        self._remove_overlay()
        logger.error("_confirm: %s | %s", title, msg)
        t = self.theme
        card = ft.Container(
            content=ft.Column([
                ft.Text(title, weight="bold", size=17, color=t.get("text"), font_family="DM Sans"),
                ft.Container(height=6),
                ft.Text(msg, size=13, color=t.get("sub"), font_family="DM Sans"),
                ft.Container(height=16),
                ft.Row([
                    ft.TextButton("Cancel", on_click=lambda e: self._remove_overlay(),
                        style=ft.ButtonStyle(color=t.get("sub"))),
                    ft.FilledButton("Confirm",
                        on_click=lambda e: [
                            self._remove_overlay(),
                            on_delete(),
                        ],
                        style=ft.ButtonStyle(
                            bgcolor=t.get("danger") if "Delete" in title or "Remove" in title or "End" in title or "Reject" in title
                                   else t.get("accent"))),
                ], alignment=ft.MainAxisAlignment.END, spacing=8),
            ], tight=True, spacing=4),
            bgcolor=t.get("card"), border_radius=18, padding=24, width=340,
            shadow=ft.BoxShadow(blur_radius=24, color="#00000055"),
            animate_opacity=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
            opacity=0,
        )
        overlay = ft.Container(
            content=card, bgcolor=ft.Colors.with_opacity(0.4, "#000"),
            alignment=ft.Alignment(0, 0), expand=True,
            on_click=lambda e: self._remove_overlay(),
            animate_opacity=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
            opacity=0,
        )
        self.page.add(overlay)
        self._active_overlay = overlay
        self.page.update()
        overlay.opacity = 1
        card.opacity = 1
        self.page.update()

    def _card(self, *controls, pad=14):
        return ft.Container(
            content=ft.Column(list(controls), spacing=10),
            bgcolor=self._clr("card"), border_radius=14,
            padding=pad,
        )

    def _stat_card(self, icon, label, value, color=None):
        c = color or self._clr("accent")
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=20, color=c),
                        bgcolor=ft.Colors.with_opacity(0.12, c),
                        width=40, height=40, border_radius=10, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text(str(value), size=22, weight="bold", color=self._clr("text"),
                                font_family="DM Sans"),
                        ft.Text(label, size=11, color=self._clr("sub"), font_family="DM Sans"),
                    ], spacing=0, tight=True),
                ], spacing=12),
            ]),
            bgcolor=self._clr("card"), border_radius=14,
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            expand=True,
        )

    def _field(self, label, hint=""):
        return ft.TextField(
            label=label, hint_text=hint,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")),
            focused_border_color=self._clr("accent"),
            label_style=ft.TextStyle(color=self._clr("sub"), size=13, font_family="DM Sans"),
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            border_radius=10, filled=True, fill_color=self._clr("card2"),
            cursor_color=self._clr("accent"),
        )

    def _btn(self, label, icon, cb, compact=False):
        return ft.FilledButton(
            content=ft.Row([
                ft.Icon(icon, size=16, color=self._clr("text")),
                ft.Text(label, size=12, weight="bold", color=self._clr("text"),
                        font_family="DM Sans"),
            ], spacing=6, tight=True),
            on_click=cb,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.1, self._clr("accent")),
                elevation=0,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding.symmetric(horizontal=14 if not compact else 10, vertical=10),
            ),
        )

    def _icon_btn(self, icon, color, tip, cb):
        return ft.IconButton(icon=icon, icon_color=color, tooltip=tip,
                             icon_size=18, on_click=cb,
                             style=ft.ButtonStyle(padding=ft.Padding.all(4)))

    def _chip(self, label, fg, bg):
        return ft.Container(
            content=ft.Text(label, size=10, color=fg, weight="bold", font_family="DM Sans"),
            bgcolor=bg, border_radius=6,
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
        )

    def _row_card(self, controls, actions=None, data=None):
        row = list(controls)
        if actions:
            row.append(ft.Row(actions, spacing=2))
        return ft.Container(
            content=ft.Row(row, spacing=12),
            bgcolor=self._clr("card"), border_radius=12,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            margin=ft.Margin.only(bottom=6),
            data=data,
        )

    def _guest_banner(self):
        if not self.is_guest: return ft.Container()
        return ft.Container(
            ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=18, color=self._clr("text")),
                ft.Text("Guest Mode \u2014 Changes are temporary. Demo sandbox, not real data.",
                        size=12, color=self._clr("text"), font_family="DM Sans", expand=True),
            ], spacing=10),
            bgcolor=ft.Colors.with_opacity(0.1, self._clr("warn")),
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            margin=ft.Margin.only(bottom=12),
        )

    # ── Tab sidebar ────────────────────────────────────────────

    def _is_mobile(self):
        return (self.page.width or 1200) < 720

    def _sidebar(self, on_select):
        mobile = self._is_mobile()
        items = []
        for i, (label, icon) in enumerate(self.TABS):
            sel = self.tab_idx["v"] == i
            items.append(ft.Container(
                content=ft.Icon(icon, size=20, color=self._clr("accent") if sel else self._clr("sub")),
                bgcolor=ft.Colors.with_opacity(0.12, self._clr("accent")) if sel else ft.Colors.TRANSPARENT,
                border_radius=10,
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                on_click=lambda e, idx=i: on_select(idx),
                tooltip=label,
            ) if mobile else ft.Container(
                ft.Row([
                    ft.Icon(icon, size=18, color=self._clr("accent") if sel else self._clr("sub")),
                    ft.Text(label, size=13, font_family="DM Sans",
                            weight="bold" if sel else "normal",
                            color=self._clr("text") if sel else self._clr("sub")),
                ], spacing=10),
                bgcolor=ft.Colors.with_opacity(0.1, self._clr("accent")) if sel else ft.Colors.TRANSPARENT,
                border_radius=12,
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                on_click=lambda e, idx=i: on_select(idx),
            ))
        if mobile:
            return ft.Container(
                content=ft.Row(items, scroll=ft.ScrollMode.AUTO, spacing=6),
                bgcolor=self._clr("card"), border_radius=14,
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
            )
        return ft.Container(
            content=ft.Column(items, spacing=4),
            bgcolor=self._clr("card"), border_radius=16,
            padding=ft.Padding.symmetric(horizontal=8, vertical=12),
            width=170,
        )

    # ════════════════════════════════════════════════════════════
    #  TAB 0 — DASHBOARD
    # ════════════════════════════════════════════════════════════

    def _round_up(self, v, step):
        if v == 0:
            return step
        return ((v // step) + (1 if v % step else 0)) * step

    def _dash_card(self, title, child):
        acc = self._clr("accent")
        acc2 = self._clr("accent2")
        return ft.Container(
            content=ft.Column([
                ft.Column([
                    ft.Text(title, size=14, weight="bold", color=self._clr("text"),
                            font_family="DM Sans"),
                    ft.Container(height=2,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                            colors=[acc, acc2, ft.Colors.with_opacity(0, acc2)],
                        ),
                        border_radius=1,
                    ),
                ], spacing=4),
                ft.Container(content=child, expand=True, margin=ft.Margin.only(top=8)),
            ], spacing=4),
            bgcolor=self._clr("card"), border_radius=16,
            padding=ft.Padding.symmetric(horizontal=18, vertical=14),
            expand=True,
            animate=ft.Animation(700, ft.AnimationCurve.EASE_OUT_BACK),
        )

    def _trunc(self, s, n):
        return (s or "?")[:n]

    def _clean_max(self, v, step=50):
        if v <= 0: return step
        return ((int(v) // step) + 1) * step

    def _nice_axis(self, max_val, target_ticks=5):
        if max_val <= 0:
            return 10, 2
        raw_step = max_val / target_ticks
        mag = 10 ** (len(str(int(raw_step))) - 1)
        norm = raw_step / mag
        if norm <= 1.5:
            nice_step = mag
        elif norm <= 3.5:
            nice_step = 2 * mag
        elif norm <= 7.5:
            nice_step = 5 * mag
        else:
            nice_step = 10 * mag
        max_y = ((max_val // nice_step) + 1) * nice_step
        return int(max_y), int(nice_step)

    def _build_ratings_chart(self, items):
        if not items:
            return ft.Text("No ratings data", color=self._clr("sub"), font_family="DM Sans")
        top = sorted(items, key=lambda x: x.get("avg_rating") or 0, reverse=True)[:8]
        groups = []
        max_count = max(((r.get("rating_count") or 1) for r in top), default=1)
        for i, r in enumerate(top):
            avg = r.get("avg_rating") or 0
            val = r.get("rating_count") or 0
            intensity = min(val / max_count, 1)
            clr = "#10B981" if avg >= 4 else "#F59E0B" if avg >= 3 else "#EF4444"
            clr = ft.Colors.with_opacity(0.6 + 0.4 * intensity, clr)
            groups.append(BarChartGroup(
                x=i,
                rods=[BarChartRod(from_y=0, to_y=avg, color=clr,
                                  tooltip=f"{r.get('Name','?')}: {avg:.1f}/5 ({val} ratings)",
                                  border_radius=6, width=22)],
            ))
        names = [self._trunc(r.get("Name"), 7) for r in top]
        return BarChart(
            groups=groups,
            group_spacing=8,
            animation=ft.Animation(800, ft.AnimationCurve.EASE_OUT_BACK),
            interactive=True,
            min_y=0, max_y=5,
            left_axis=ChartAxis(
                title="Rating", title_size=12, show_labels=True,
                label_size=40,
                labels=[
                    ChartAxisLabel(v, ft.Text(str(v), size=12, color=self._clr("text"),
                                              font_family="DM Sans", no_wrap=True))
                    for v in range(0, 6)
                ],
            ),
            bottom_axis=ChartAxis(
                labels=[ChartAxisLabel(i, ft.Text(n, size=11, color=self._clr("text"),
                                                  font_family="DM Sans"))
                        for i, n in enumerate(names)],
                show_labels=True, label_size=90,
            ),
        )

    def _build_price_cost_line(self, items):
        if not items:
            return ft.Text("No food data", color=self._clr("sub"), font_family="DM Sans")
        top = sorted(items, key=lambda x: x.get("Price") or 0, reverse=True)[:8]
        price_points = []
        cost_points = []
        for i, f in enumerate(top):
            price = f.get("Price") or 0
            cost = f.get("Estimated_Cost") or price * 0.6
            price_points.append(LineChartDataPoint(x=i, y=price,
                tooltip=f"{f.get('Name','?')}: PKR {price:,.0f}"))
            cost_points.append(LineChartDataPoint(x=i, y=cost,
                tooltip=f"Cost: PKR {cost:,.0f}"))
        max_v = max(((f.get("Price") or 0) for f in top), default=100)
        max_y, step = self._nice_axis(max_v, 5)
        names = [self._trunc(f.get("Name"), 7) for f in top]
        n = len(price_points)
        return LineChart(
            data_series=[
                LineChartData(
                    points=price_points, color="#3B82F6", stroke_width=3,
                    curved=True, point=ChartCirclePoint(radius=5),
                    below_line_bgcolor=ft.Colors.with_opacity(0.08, "#3B82F6"),
                    below_line_cutoff_y=0,
                ),
                LineChartData(
                    points=cost_points, color="#8B5CF6", stroke_width=3,
                    curved=True, point=ChartCirclePoint(radius=5),
                    below_line_bgcolor=ft.Colors.with_opacity(0.08, "#8B5CF6"),
                    below_line_cutoff_y=0,
                ),
            ],
            min_x=-0.3, max_x=n - 0.7,
            min_y=0, max_y=max_y,
            animation=ft.Animation(800, ft.AnimationCurve.EASE_OUT_BACK),
            interactive=True,
            left_axis=ChartAxis(
                title="PKR", title_size=12, show_labels=True,
                label_size=40,
                labels=[
                    ChartAxisLabel(v, ft.Text(str(v), size=12, color=self._clr("text"),
                                              font_family="DM Sans", no_wrap=True))
                    for v in range(0, max_y + 1, step)
                ],
            ),
            bottom_axis=ChartAxis(
                labels=[ChartAxisLabel(i, ft.Text(n, size=11, color=self._clr("text"),
                                                  font_family="DM Sans"))
                        for i, n in enumerate(names)],
                show_labels=True, label_size=90,
            ),
        )

    def _build_stock_chart(self, items):
        if not items:
            return ft.Text("No ingredients", color=self._clr("sub"), font_family="DM Sans")
        top = sorted(items, key=lambda x: x.get("Total_Quantity") or 0)[:10]
        groups = []
        for i, ing in enumerate(top):
            qty = ing.get("Total_Quantity") or 0
            unit = ing.get("Unit") or ""
            is_low = qty < 10
            clr = "#EF4444" if is_low else "#F59E0B" if qty < 25 else "#10B981"
            groups.append(BarChartGroup(
                x=i,
                rods=[BarChartRod(from_y=0, to_y=qty, color=clr,
                                  tooltip=f"{ing.get('Name','?')}: {qty} {unit}",
                                  border_radius=6, width=18)],
            ))
        names = [self._trunc(ing.get("Name"), 7) for ing in top]
        max_q = max(((i.get("Total_Quantity") or 0) for i in top), default=10)
        max_y, step = self._nice_axis(max_q, 5)
        return BarChart(
            groups=groups,
            group_spacing=6,
            animation=ft.Animation(800, ft.AnimationCurve.EASE_OUT_BACK),
            interactive=True,
            min_y=0, max_y=max_y,
            left_axis=ChartAxis(
                title="Stock", title_size=12, show_labels=True,
                label_size=40,
                labels=[
                    ChartAxisLabel(v, ft.Text(str(v), size=12, color=self._clr("text"),
                                              font_family="DM Sans", no_wrap=True))
                    for v in range(0, max_y + 1, step)
                ],
            ),
            bottom_axis=ChartAxis(
                labels=[ChartAxisLabel(i, ft.Text(n, size=11, color=self._clr("text"),
                                                  font_family="DM Sans"))
                        for i, n in enumerate(names)],
                show_labels=True, label_size=90,
            ),
        )

    def _build_menu_ratings_line(self, items):
        if not items:
            return ft.Text("No menu data", color=self._clr("sub"), font_family="DM Sans")
        top = sorted(items, key=lambda x: x.get("Schedule_ID") or 0)[:12]
        pts = []
        for i, m in enumerate(top):
            r = m.get("Ratings_Average") or 0
            nm = m.get("Food_Item_Name") or m.get("meal_type", "?") or "?"
            pts.append(LineChartDataPoint(x=i, y=r,
                tooltip=f"{nm}: {r:.1f}/5"))
        names = [self._trunc(m.get("Food_Item_Name") or m.get("meal_type", "?"), 7) for m in top]
        max_y = 5.0
        n = len(pts)
        return LineChart(
            data_series=[
                LineChartData(
                    points=pts, color="#F59E0B", stroke_width=3,
                    curved=True, point=ChartCirclePoint(radius=5),
                    below_line_bgcolor=ft.Colors.with_opacity(0.08, "#F59E0B"),
                    below_line_cutoff_y=0,
                ),
            ],
            min_x=-0.3, max_x=n - 0.7,
            min_y=0, max_y=max_y,
            animation=ft.Animation(800, ft.AnimationCurve.EASE_OUT_BACK),
            interactive=True,
            left_axis=ChartAxis(
                title="Rating", title_size=12, show_labels=True,
                label_size=40,
                labels=[
                    ChartAxisLabel(v, ft.Text(str(v), size=11, color=self._clr("text"),
                                              font_family="DM Sans"))
                    for v in range(0, 6)
                ],
            ),
            bottom_axis=ChartAxis(
                labels=[ChartAxisLabel(i, ft.Text(n, size=11, color=self._clr("text"),
                                                  font_family="DM Sans"))
                        for i, n in enumerate(names)],
                show_labels=True, label_size=90,
            ),
        )

    def _build_population_pie(self, students, staff):
        total = students + staff
        if total == 0:
            return ft.Text("No user data", color=self._clr("sub"), font_family="DM Sans")
        sections = [
            PieChartSection(value=students / total * 100, color="#3B82F6",
                            title=f"Students ({students})", radius=70,
                            title_style=ft.TextStyle(size=11, color=self._clr("text"), font_family="DM Sans")),
            PieChartSection(value=staff / total * 100, color="#8B5CF6",
                            title=f"Staff ({staff})", radius=70,
                            title_style=ft.TextStyle(size=11, color=self._clr("text"), font_family="DM Sans")),
        ]
        return PieChart(
            sections=sections,
            sections_space=3,
            center_space_radius=25,
            animation=ft.Animation(900, ft.AnimationCurve.EASE_OUT_BACK),
        )

    def _build_billing_line(self, bills):
        if not bills:
            return ft.Text("No billing data", color=self._clr("sub"), font_family="DM Sans")
        monthly = {}
        for b in bills:
            month = b.get("Billing_Month") or b.get("Month") or "Unknown"
            if month not in monthly:
                monthly[month] = {"collected": 0, "outstanding": 0}
            monthly[month]["collected"] += b.get("Total_Collected") or 0
            monthly[month]["outstanding"] += b.get("Outstanding") or 0
        sorted_months = sorted(monthly.keys())
        first = sorted_months[0]
        last = sorted_months[-1]
        try:
            from calendar import monthrange
            y1, m1 = int(first[:4]), int(first[5:7])
            y2, m2 = int(last[:4]), int(last[5:7])
            all_months = []
            y, m = y1, m1
            while (y < y2) or (y == y2 and m <= m2):
                all_months.append(f"{y}-{m:02d}")
                m += 1
                if m > 12:
                    m = 1
                    y += 1
        except (ValueError, IndexError):
            all_months = sorted_months
        collected_points = []
        outstanding_points = []
        for i, m in enumerate(all_months):
            d = monthly.get(m, {"collected": 0, "outstanding": 0})
            collected_points.append(LineChartDataPoint(
                x=i, y=d["collected"],
                tooltip=f"{m}: PKR {d['collected']:,.0f} collected",
            ))
            outstanding_points.append(LineChartDataPoint(
                x=i, y=d["outstanding"],
                tooltip=f"{m}: PKR {d['outstanding']:,.0f} outstanding",
            ))
        max_val = max(
            max((d["collected"] for d in monthly.values()), default=0),
            max((d["outstanding"] for d in monthly.values()), default=0),
        ) or 1
        max_y, step = self._nice_axis(max_val, 5)
        month_labels = [m[-2:] for m in all_months]
        n = len(collected_points)
        return LineChart(
            data_series=[
                LineChartData(
                    points=collected_points, color="#10B981", stroke_width=3,
                    curved=True, point=ChartCirclePoint(radius=5),
                    below_line_bgcolor=ft.Colors.with_opacity(0.08, "#10B981"),
                    below_line_cutoff_y=0,
                ),
                LineChartData(
                    points=outstanding_points, color="#EF4444", stroke_width=3,
                    curved=True, point=ChartCirclePoint(radius=5),
                    below_line_bgcolor=ft.Colors.with_opacity(0.08, "#EF4444"),
                    below_line_cutoff_y=0,
                ),
            ],
            min_x=-0.3, max_x=n - 0.7,
            min_y=0, max_y=max_y,
            animation=ft.Animation(800, ft.AnimationCurve.EASE_OUT_BACK),
            interactive=True,
            left_axis=ChartAxis(
                title="PKR", title_size=12, show_labels=True,
                label_size=40,
                labels=[
                    ChartAxisLabel(v, ft.Text(f"{v:,.0f}", size=12, color=self._clr("text"),
                                              font_family="DM Sans", no_wrap=True))
                    for v in range(0, max_y + 1, step)
                ],
            ),
            bottom_axis=ChartAxis(
                labels=[
                    ChartAxisLabel(i, ft.Text(m, size=11, color=self._clr("text"),
                                              font_family="DM Sans"))
                    for i, m in enumerate(month_labels)
                ],
                show_labels=True, label_size=60,
            ),
        )

    def _build_activity_trend(self, activity_data):
        if not activity_data:
            return ft.Text("No activity data", color=self._clr("sub"), font_family="DM Sans")
        daily = {}
        for a in activity_data:
            dt = a.get("event_date", "")
            if isinstance(dt, str) and "T" in dt:
                dt = dt[:10]
            if dt not in daily:
                daily[dt] = 0
            daily[dt] += 1
        sorted_dates = sorted(daily.keys())[:14]
        pts = []
        for i, d in enumerate(sorted_dates):
            pts.append(LineChartDataPoint(x=i, y=daily[d],
                tooltip=f"{d}: {daily[d]} events"))
        max_c = max((daily[d] for d in sorted_dates), default=5)
        max_y, step = self._nice_axis(max_c, 5)
        date_labels = [d[-5:] for d in sorted_dates]
        n = len(pts)
        return LineChart(
            data_series=[
                LineChartData(
                    points=pts, color="#3B82F6", stroke_width=3,
                    curved=True, point=ChartCirclePoint(radius=5),
                    below_line_bgcolor=ft.Colors.with_opacity(0.08, "#3B82F6"),
                    below_line_cutoff_y=0,
                ),
            ],
            min_x=-0.3, max_x=n - 0.7,
            min_y=0, max_y=max_y,
            animation=ft.Animation(800, ft.AnimationCurve.EASE_OUT_BACK),
            interactive=True,
            left_axis=ChartAxis(
                title="Events", title_size=12, show_labels=True,
                label_size=40,
                labels=[
                    ChartAxisLabel(v, ft.Text(str(v), size=12, color=self._clr("text"),
                                              font_family="DM Sans", no_wrap=True))
                    for v in range(0, max_y + 1, step)
                ],
            ),
            bottom_axis=ChartAxis(
                labels=[ChartAxisLabel(i, ft.Text(d, size=10, color=self._clr("text"),
                                                  font_family="DM Sans"))
                        for i, d in enumerate(date_labels)],
                show_labels=True, label_size=75,
            ),
        )

    def _build_cost_profile_line(self, ingredients):
        if not ingredients:
            return ft.Text("No ingredient data", color=self._clr("sub"), font_family="DM Sans")
        top = sorted(ingredients, key=lambda x: x.get("Unit_cost") or 0, reverse=True)[:10]
        pts = []
        for i, ing in enumerate(top):
            cost = ing.get("Unit_cost") or 0
            qty = ing.get("Total_Quantity") or 0
            pts.append(LineChartDataPoint(x=i, y=cost,
                tooltip=f"{ing.get('Name','?')}: PKR {cost}/unit ({qty} {ing.get('Unit','')})"))
        names = [self._trunc(ing.get("Name"), 7) for ing in top]
        max_c = max((p.y for p in pts), default=100)
        max_y, step = self._nice_axis(max_c, 5)
        n = len(pts)
        return LineChart(
            data_series=[
                LineChartData(
                    points=pts, color="#8B5CF6", stroke_width=3,
                    curved=True, point=ChartCirclePoint(radius=5),
                    below_line_bgcolor=ft.Colors.with_opacity(0.08, "#8B5CF6"),
                    below_line_cutoff_y=0,
                ),
            ],
            min_x=-0.3, max_x=n - 0.7,
            min_y=0, max_y=max_y,
            animation=ft.Animation(800, ft.AnimationCurve.EASE_OUT_BACK),
            interactive=True,
            left_axis=ChartAxis(
                title="PKR/unit", title_size=12, show_labels=True,
                label_size=40,
                labels=[
                    ChartAxisLabel(v, ft.Text(str(v), size=12, color=self._clr("text"),
                                              font_family="DM Sans", no_wrap=True))
                    for v in range(0, max_y + 1, step)
                ],
            ),
            bottom_axis=ChartAxis(
                labels=[ChartAxisLabel(i, ft.Text(n, size=11, color=self._clr("text"),
                                                  font_family="DM Sans"))
                        for i, n in enumerate(names)],
                show_labels=True, label_size=90,
            ),
        )

    async def _render_dashboard(self, ref):
        ref.content = self._loading()
        self.page.update()

        stats = {"total_students": 0, "total_staff": 0, "total_food_items": 0,
                 "total_ingredients": 0, "active_mess_offs": 0, "unpaid_bills": 0,
                 "pending_registration_requests": 0}
        activity = []
        ratings = []
        ingredients = []
        food_items_data = []
        menu_items = []
        bills_data = []
        low_stock = []

        if not self.is_guest:
            s = await _api("stats")["dashboard"](self.email)
            if isinstance(s, dict) and "error" not in s:
                stats = s
            act = await _api("stats")["activity"](self.email)
            if isinstance(act, list):
                activity = act
            r = await _api("analytics")["ratings"](self.email)
            if isinstance(r, list):
                ratings = r
            ing = await _api("ingredients")["all"](self.email)
            if isinstance(ing, list):
                ingredients = ing
            fc = await _api("food")["all"](self.email)
            if isinstance(fc, list):
                food_items_data = fc
            mv = await _api("menu")["weekly"](self.email)
            if isinstance(mv, list):
                menu_items = mv
            bl = await _api("analytics")["billing"](self.email)
            if isinstance(bl, list):
                bills_data = bl
            ls = await _api("analytics")["low_stock"](self.email)
            if isinstance(ls, list):
                low_stock = ls
        else:
            stats = {
                **stats,
                "total_students": len(mock_data.get_students()),
                "total_staff": len(mock_data.get_staff()),
                "total_food_items": len(mock_data.get_food_costs()),
                "total_ingredients": len(mock_data.get_ingredients()),
                "active_mess_offs": len([m for m in mock_data.get_mess_off_history().get("status", []) if m.get("Status") == "Pending"]),
                "unpaid_bills": len([b for b in mock_data.get_monthly_bills() if b.get("Status") != "Paid"]),
                "pending_registration_requests": len(mock_data.get_registration_requests()),
            }
            ratings = mock_data.get_food_ratings()
            ingredients = mock_data.get_ingredients()
            food_items_data = mock_data.get_food_costs()
            menu_items = mock_data.get_weekly_menu()
            bills_data = mock_data.get_monthly_billing_summary()
            low_stock = mock_data.get_low_stock_ingredients()
            from datetime import timedelta
            today = date.today()
            activity = [
                {"description": "New student registration: New Student", "event_date": (today - timedelta(days=i)).isoformat()}
                for i in range(7)
            ] + [
                {"description": f"Bill payment: PKR {a*500}", "event_date": (today - timedelta(days=i)).isoformat()}
                for i, a in enumerate([3, 5, 2, 4, 1, 6, 3])
            ]

        t = self.theme
        ac = t.get("accent", "#3B82F6")
        ac2 = t.get("accent2", "#8B5CF6")
        sc = t.get("success", "#10B981")
        wa = t.get("warn", "#F59E0B")
        da = t.get("danger", "#EF4444")

        def _sc(icon, label, value, color):
            c = color or ac
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(icon, size=18, color=c),
                            bgcolor=ft.Colors.with_opacity(0.12, c),
                            width=36, height=36, border_radius=10, alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column([
                            ft.Text(str(value), size=20, weight="bold",
                                    color=t.get("text"), font_family="DM Sans"),
                            ft.Text(label, size=10, color=t.get("sub"), font_family="DM Sans"),
                        ], spacing=0, tight=True),
                    ], spacing=10),
                ]),
                bgcolor=t.get("card"), border_radius=14,
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                expand=True,
            )

        stat_cards = ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(_sc(ft.Icons.SCHOOL_ROUNDED, "Students", stats["total_students"], ac), col={"sm": 4}),
                ft.Container(_sc(ft.Icons.BADGE_ROUNDED, "Staff", stats["total_staff"], ac2), col={"sm": 4}),
                ft.Container(_sc(ft.Icons.FASTFOOD_ROUNDED, "Food Items", stats["total_food_items"], sc), col={"sm": 4}),
                ft.Container(_sc(ft.Icons.CATEGORY_ROUNDED, "Ingredients", stats["total_ingredients"], wa), col={"sm": 3}),
                ft.Container(_sc(ft.Icons.EVENT_BUSY_ROUNDED, "Active Mess Offs", stats["active_mess_offs"], da), col={"sm": 3}),
                ft.Container(_sc(ft.Icons.RECEIPT_ROUNDED, "Unpaid Bills", stats["unpaid_bills"], wa), col={"sm": 3}),
                ft.Container(_sc(ft.Icons.PERSON_ADD_ALT_1_ROUNDED, "Pending Reg.", stats["pending_registration_requests"], ac2), col={"sm": 3}),
            ], spacing=10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
        )

        ratings_chart = self._build_ratings_chart(ratings)
        cost_chart = self._build_price_cost_line(food_items_data)
        stock_chart = self._build_stock_chart(ingredients)
        menu_ratings_chart = self._build_menu_ratings_line(menu_items)
        population_pie = self._build_population_pie(stats.get("total_students", 0), stats.get("total_staff", 0))
        billing_chart = self._build_billing_line(bills_data)
        activity_chart = self._build_activity_trend(activity)
        cost_profile_chart = self._build_cost_profile_line(ingredients)

        activity_section = ft.Container()
        if activity:
            feed_rows = []
            for a in activity:
                desc = a.get("description", "")
                dt = a.get("event_date", "")
                dty = datetime.fromisoformat(str(dt)) if isinstance(dt, str) and "T" in str(dt) else str(dt)[:10]
                feed_rows.append(ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.CIRCLE_ROUNDED, size=8, color=ac),
                        margin=ft.Margin.only(top=4),
                    ),
                    ft.Container(
                        content=ft.Text(desc, size=12, color=t.get("text"),
                                        font_family="DM Sans", expand=True),
                        expand=True,
                    ),
                    ft.Text(str(dty)[:10], size=10, color=t.get("sub"), font_family="DM Sans"),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START))
            activity_section = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.HISTORY_ROUNDED, size=18, color=ac),
                        ft.Text("Recent Activity", size=15, weight="bold",
                                color=t.get("text"), font_family="DM Sans"),
                    ], spacing=8),
                    ft.Container(height=4),
                    ft.Column(feed_rows, spacing=6),
                ]),
                bgcolor=t.get("card"), border_radius=16,
                padding=14,
            )

        low_stock_section = ft.Container()
        if low_stock:
            ls_rows = []
            for ing in low_stock[:5]:
                nm = ing.get("Name") or "?"
                qty = ing.get("Total_Quantity") or 0
                unit = ing.get("Unit") or ""
                ls_rows.append(ft.Row([
                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=16, color=da),
                    ft.Text(f"{nm}: {qty} {unit}", size=12, color=t.get("text"),
                            font_family="DM Sans", expand=True),
                ], spacing=8))
            low_stock_section = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INVENTORY_ROUNDED, size=18, color=da),
                        ft.Text(f"Low Stock Alert ({len(low_stock)})", size=15, weight="bold",
                                color=t.get("text"), font_family="DM Sans"),
                    ], spacing=8),
                    ft.Container(height=4),
                    ft.Column(ls_rows, spacing=4),
                ]),
                bgcolor=ft.Colors.with_opacity(0.08, da),
                border_radius=16,
                padding=14,
                border=ft.border.all(1, ft.Colors.with_opacity(0.2, da)),
            )

        _anim_queue = []

        def _fade_wrap(child, delay):
            c = ft.Container(
                content=child, expand=True,
                opacity=0,
                animate_opacity=ft.Animation(500 + delay * 120, ft.AnimationCurve.EASE_OUT),
            )
            _anim_queue.append(c)
            return c

        def _section(title, icon, delay):
            c = ft.Container(
                content=ft.Row([
                    ft.Icon(icon, size=18, color=ac),
                    ft.Text(title, size=15, weight="bold",
                            color=t.get("text"), font_family="DM Sans"),
                ], spacing=8),
                opacity=0,
                animate_opacity=ft.Animation(400 + delay * 120, ft.AnimationCurve.EASE_OUT),
            )
            _anim_queue.append(c)
            return c

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([
                ft.Column([
                    ft.Text("Dashboard", size=22, weight="bold",
                            color=t.get("text"), font_family="DM Sans"),
                    ft.Text("Deep analytics & insights", size=12,
                            color=t.get("sub"), font_family="DM Sans"),
                ]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=12),
            stat_cards,
            ft.Container(height=16),
            _section("Food Analytics", ft.Icons.RESTAURANT_ROUNDED, 0),
            ft.Container(height=8),
            ft.ResponsiveRow([
                ft.Container(_fade_wrap(self._dash_card("Avg Ratings (top 8)", ratings_chart), 1),
                             col={"sm": 12, "md": 6}),
                ft.Container(_fade_wrap(self._dash_card("Price vs Cost Trend", cost_chart), 2),
                             col={"sm": 12, "md": 6}),
            ], spacing=12),
            ft.Container(height=16),
            _section("Inventory & Menu", ft.Icons.INVENTORY_ROUNDED, 3),
            ft.Container(height=8),
            ft.ResponsiveRow([
                ft.Container(_fade_wrap(self._dash_card("Stock Levels (lowest 10)", stock_chart), 4),
                             col={"sm": 12, "md": 6}),
                ft.Container(_fade_wrap(self._dash_card("Menu Ratings Trend", menu_ratings_chart), 5),
                             col={"sm": 12, "md": 6}),
            ], spacing=12),
            ft.Container(height=16),
            _section("People & Finance", ft.Icons.ACCOUNT_BALANCE_ROUNDED, 6),
            ft.Container(height=8),
            ft.ResponsiveRow([
                ft.Container(_fade_wrap(self._dash_card("Population Distribution", population_pie), 7),
                             col={"sm": 12, "md": 6}),
                ft.Container(_fade_wrap(self._dash_card("Billing Trend (monthly)", billing_chart), 8),
                             col={"sm": 12, "md": 6}),
            ], spacing=12),
            ft.Container(height=16),
            _section("Operational Trends", ft.Icons.TRENDING_UP_ROUNDED, 9),
            ft.Container(height=8),
            ft.ResponsiveRow([
                ft.Container(_fade_wrap(self._dash_card("Daily Activity Trend", activity_chart), 10),
                             col={"sm": 12, "md": 6}),
                ft.Container(_fade_wrap(self._dash_card("Ingredient Cost Profile", cost_profile_chart), 11),
                             col={"sm": 12, "md": 6}),
            ], spacing=12),
            ft.Container(height=16),
            ft.ResponsiveRow([
                ft.Container(activity_section, col={"sm": 12, "md": 7 if low_stock else 12}),
                ft.Container(low_stock_section, col={"sm": 12, "md": 5}) if low_stock else ft.Container(),
            ], spacing=12) if activity or low_stock else ft.Container(),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

        async def _stagger():
            for i, c in enumerate(_anim_queue):
                await asyncio.sleep(0.08)
                c.opacity = 1
                self.page.update()
        asyncio.create_task(_stagger())

    # ════════════════════════════════════════════════════════════
    #  TAB 1 — STUDENTS
    # ════════════════════════════════════════════════════════════

    async def _render_students(self, ref):
        ref.content = self._loading(); self.page.update()
        students = (mock_data.get_students() if self.is_guest
                    else [u for u in _ensure_list(await _api("students")["all"](self.email)) if u.get("Account_Type") == "Student"])

        search_bar = ft.TextField(
            hint_text="Search by name or email\u2026", prefix_icon=ft.Icons.SEARCH_ROUNDED,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")),
            border_radius=10, filled=True, fill_color=self._clr("card2"),
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            on_change=lambda e: _filter(e.data),
            expand=True,
        )

        def _filter(q):
            q = q.lower()
            for c in student_rows.controls:
                c.visible = q in (c.data or "").lower() if q else True
            self.page.update()

        student_rows = ft.Column(spacing=4)

        async def refresh():
            await self._render_students(ref)

        for s in students:
            uid = s.get("UserID")
            name = f"{s.get('First_Name','')} {s.get('Last_Name','')}"
            email = s.get("Email", "")
            label = f"{name} | {email} | {uid}"
            def do_del(e, u=uid):
                if self.is_guest:
                    mock_data.delete_student(u)
                    self._snack("Deleted")
                    asyncio.create_task(refresh())
                else:
                    self._confirm("Delete Student", f"Remove {name}?", lambda: self._run(_del_student(u)))
            async def _del_student(u=uid):
                r = await _api("students")["delete"](self.email, u)
                if "error" in (r or {}): logger.error("del_student %s: %s", u, r["error"]); self._snack(r["error"], False); return
                self._snack("Deleted"); await refresh()
            student_rows.controls.append(self._row_card([
                ft.Column([
                    ft.Text(name, size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(email, size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._icon_btn(ft.Icons.DELETE_ROUNDED, self._clr("danger"), "Delete", do_del),
            ], data=label))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Students", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Row([search_bar], spacing=8),
            ft.Container(height=4),
            ft.Row([self._btn("Refresh", ft.Icons.REFRESH_ROUNDED, lambda e: asyncio.create_task(refresh()))], alignment=ft.MainAxisAlignment.END),
            ft.Container(height=4),
            student_rows if student_rows.controls else ft.Text("No students found", color=self._clr("sub"), font_family="DM Sans"),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 2 — STAFF
    # ════════════════════════════════════════════════════════════

    async def _render_staff(self, ref):
        ref.content = self._loading(); self.page.update()
        staff_list = (mock_data.get_staff() if self.is_guest
                      else [u for u in _ensure_list(await _api("staff")["all"](self.email)) if u.get("Account_Type") == "Staff"])

        search_bar = ft.TextField(
            hint_text="Search staff\u2026", prefix_icon=ft.Icons.SEARCH_ROUNDED,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")),
            border_radius=10, filled=True, fill_color=self._clr("card2"),
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            on_change=lambda e: _filter(e.data),
            expand=True,
        )

        def _filter(q):
            q = q.lower()
            for c in staff_rows.controls:
                c.visible = q in (c.data or "").lower() if q else True
            self.page.update()

        staff_rows = ft.Column(spacing=4)

        async def refresh():
            await self._render_staff(ref)

        for s in staff_list:
            uid = s.get("UserID")
            name = f"{s.get('First_Name','')} {s.get('Last_Name','')}"
            email = s.get("Email", "")
            label = f"{name} | {email} | {uid}"
            def do_del(e, u=uid):
                if self.is_guest:
                    mock_data.delete_staff(u)
                    self._snack("Deleted")
                    asyncio.create_task(refresh())
                else:
                    self._confirm("Delete Staff", f"Remove {name}?", lambda: self._run(_del_staff(u)))
            async def _del_staff(u=uid):
                r = await _api("staff")["delete"](self.email, u)
                if "error" in (r or {}): logger.error("del_staff %s: %s", u, r["error"]); self._snack(r["error"], False); return
                self._snack("Deleted"); await refresh()
            staff_rows.controls.append(self._row_card([
                ft.Column([
                    ft.Text(name, size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(email, size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._icon_btn(ft.Icons.DELETE_ROUNDED, self._clr("danger"), "Delete", do_del),
            ], data=label))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Staff", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Row([search_bar], spacing=8),
            ft.Row([self._btn("Refresh", ft.Icons.REFRESH_ROUNDED, lambda e: asyncio.create_task(refresh()))], alignment=ft.MainAxisAlignment.END),
            staff_rows if staff_rows.controls else ft.Text("No staff found", color=self._clr("sub"), font_family="DM Sans"),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 3 — FOOD ITEMS
    # ════════════════════════════════════════════════════════════

    async def _render_food(self, ref):
        ref.content = self._loading(); self.page.update()
        items = (mock_data.get_food_costs() if self.is_guest
                 else (await _api("food")["all"](self.email)) or [])

        search_bar = ft.TextField(
            hint_text="Search food items\u2026", prefix_icon=ft.Icons.SEARCH_ROUNDED,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")),
            border_radius=10, filled=True, fill_color=self._clr("card2"),
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            on_change=lambda e: _filter(e.data), expand=True,
        )

        def _filter(q):
            q = q.lower()
            for c in food_rows.controls:
                c.visible = q in (c.data or "").lower() if q else True
            self.page.update()

        food_rows = ft.Column(spacing=4)

        async def refresh():
            await self._render_food(ref)

        mobile = self._is_mobile()

        # ── add food form ──────────────────────────────────
        add_f_name  = ft.TextField(hint_text="Name", dense=True, expand=True,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")), border_radius=8,
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            filled=True, fill_color=self._clr("card"),)
        add_f_price = ft.TextField(hint_text="Price", dense=True, expand=mobile, width=90 if not mobile else None,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")), border_radius=8,
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            filled=True, fill_color=self._clr("card"),)
        add_f_qty   = ft.TextField(hint_text="Qty", dense=True, expand=mobile, width=60 if not mobile else None,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")), border_radius=8,
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            text_align=ft.TextAlign.CENTER, filled=True, fill_color=self._clr("card"),)

        add_f_form = ft.Container(
            content=ft.Column([
                ft.Row([add_f_name, add_f_price, add_f_qty], spacing=6, wrap=mobile),
                ft.Row([
                    self._btn("Save", ft.Icons.SAVE_ROUNDED,
                              lambda e: asyncio.create_task(do_add_food(e))),
                    self._btn("Cancel", ft.Icons.CLOSE_ROUNDED, lambda e: do_toggle_add_f(e)),
                ], alignment=ft.MainAxisAlignment.END),
            ], spacing=8),
            visible=False, margin=ft.Margin.only(bottom=6),
        )

        def do_toggle_add_f(e):
            add_f_form.visible = not add_f_form.visible
            if not add_f_form.visible:
                add_f_name.value = add_f_price.value = add_f_qty.value = ""
            self.page.update()

        async def do_add_food(e):
            try:
                data = {
                    "Name": add_f_name.value.strip(),
                    "Price": float(add_f_price.value or 0),
                    "Quantity": float(add_f_qty.value or 0),
                }
            except ValueError:
                self._snack("Invalid number", False); return
            if not data["Name"]:
                self._snack("Name required", False); return
            if self.is_guest:
                mock_data.create_food(data)
                self._snack("Created")
                await refresh()
            else:
                r = await _api("food")["create"](self.email, data)
                if "error" in (r or {}): logger.error("create_food: %s", r["error"]); self._snack(r["error"], False); return
                self._snack("Created"); await refresh()

        header = ft.Container(
            ft.Row([
                ft.Text("Name", size=11, weight="bold", color=self._clr("sub"), font_family="DM Sans", expand=True),
                ft.Text("Price", size=11, weight="bold", color=self._clr("sub"), font_family="DM Sans", width=90, text_align=ft.TextAlign.CENTER),
                ft.Text("Qty", size=11, weight="bold", color=self._clr("sub"), font_family="DM Sans", width=60, text_align=ft.TextAlign.CENTER),
                ft.Container(width=72),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self._clr("card"), border_radius=12,
            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
            margin=ft.Margin.only(bottom=4),
            visible=not self._is_mobile(),
        )

        for item in items:
            iid = item.get("Item_ID")
            name = item.get("Name", "")
            price = item.get("Price", 0)
            qty = item.get("Quantity", 0)
            label = f"{name} | {iid}"

            ef_name  = ft.TextField(value=name, expand=True, dense=True,
                border_color=self._clr("accent"), border_radius=8,
                text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
                filled=True, fill_color=self._clr("card"),)
            ef_price = ft.TextField(value=str(price), expand=mobile, width=90 if not mobile else None, dense=True,
                border_color=self._clr("accent"), border_radius=8,
                text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
                filled=True, fill_color=self._clr("card"),)
            ef_qty   = ft.TextField(value=str(qty), expand=mobile, width=60 if not mobile else None, dense=True,
                border_color=self._clr("accent"), border_radius=8,
                text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
                text_align=ft.TextAlign.CENTER,
                filled=True, fill_color=self._clr("card"),)

            def do_upd(e, i=iid, nf=ef_name, pf=ef_price, qf=ef_qty):
                try:
                    p = {"Name": nf.value, "Price": float(pf.value or 0), "Quantity": float(qf.value or 0)}
                except ValueError:
                    self._snack("Invalid number", False); return
                if self.is_guest:
                    mock_data.update_food(i, p)
                    self._snack("Updated")
                else:
                    self._run(_upd_food(i, p))
            async def _upd_food(i=iid, p=None):
                r = await _api("food")["update"](self.email, i, p)
                if "error" in (r or {}): logger.error("upd_food %s: %s", i, r["error"]); self._snack(r["error"], False); return
                self._snack("Updated")

            def do_del(e, i=iid):
                if self.is_guest:
                    mock_data.delete_food(i)
                    self._snack("Deleted")
                    asyncio.create_task(refresh())
                else:
                    self._confirm("Delete Food Item", f"Remove {name}?", lambda: self._run(_del_food(i)))
            async def _del_food(i=iid):
                r = await _api("food")["delete"](self.email, i)
                if "error" in (r or {}): logger.error("del_food %s: %s", i, r["error"]); self._snack(r["error"], False); return
                self._snack("Deleted"); await refresh()

            if mobile:
                food_rows.controls.append(ft.Container(
                    content=ft.Column([
                        ef_name,
                        ft.Row([ef_price, ef_qty], spacing=6),
                        ft.Row([
                            self._icon_btn(ft.Icons.SAVE_ROUNDED, self._clr("accent"), "Save", do_upd),
                            self._icon_btn(ft.Icons.DELETE_ROUNDED, self._clr("danger"), "Delete", do_del),
                        ], alignment=ft.MainAxisAlignment.END),
                    ], spacing=6),
                    bgcolor=self._clr("card"), border_radius=12,
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    margin=ft.Margin.only(bottom=6),
                    data=label,
                ))
            else:
                food_rows.controls.append(self._row_card([
                    ef_name, ef_price,
                    ef_qty,
                ], actions=[
                self._icon_btn(ft.Icons.SAVE_ROUNDED, self._clr("accent"), "Save", do_upd),
                self._icon_btn(ft.Icons.DELETE_ROUNDED, self._clr("danger"), "Delete", do_del),
            ], data=label))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([
                ft.Text("Food Items", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                self._btn("Add Item", ft.Icons.ADD_ROUNDED, do_toggle_add_f),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Row([search_bar], spacing=8),
            add_f_form,
            ft.Row([self._btn("Refresh", ft.Icons.REFRESH_ROUNDED, lambda e: asyncio.create_task(refresh()))], alignment=ft.MainAxisAlignment.END),
            header,
            food_rows if food_rows.controls else ft.Text("No food items", color=self._clr("sub"), font_family="DM Sans"),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 4 — INGREDIENTS
    # ════════════════════════════════════════════════════════════

    async def _render_ingredients(self, ref):
        ref.content = self._loading(); self.page.update()
        items = (mock_data.get_ingredients() if self.is_guest
                 else _ensure_list(await _api("ingredients")["all"](self.email)))

        search_bar = ft.TextField(
            hint_text="Search ingredients\u2026", prefix_icon=ft.Icons.SEARCH_ROUNDED,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")),
            border_radius=10, filled=True, fill_color=self._clr("card2"),
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            on_change=lambda e: _filter(e.data), expand=True,
        )

        def _filter(q):
            q = q.lower()
            for c in ing_rows.controls:
                c.visible = q in (c.data or "").lower() if q else True
            self.page.update()

        ing_rows = ft.Column(spacing=4)

        mobile = self._is_mobile()

        # ── fields for add form ──────────────────────────────
        add_name   = ft.TextField(hint_text="Name", dense=True, expand=True,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")), border_radius=8,
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            filled=True, fill_color=self._clr("card"),)
        add_qty    = ft.TextField(hint_text="Qty", dense=True, expand=mobile, width=70 if not mobile else None,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")), border_radius=8,
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            text_align=ft.TextAlign.CENTER, filled=True, fill_color=self._clr("card"),)
        add_unit   = ft.TextField(hint_text="Unit", dense=True, expand=mobile, width=60 if not mobile else None,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")), border_radius=8,
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            text_align=ft.TextAlign.CENTER, filled=True, fill_color=self._clr("card"),)
        add_cost   = ft.TextField(hint_text="Cost/unit", dense=True, expand=mobile, width=90 if not mobile else None,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")), border_radius=8,
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            text_align=ft.TextAlign.CENTER, filled=True, fill_color=self._clr("card"),)

        add_form = ft.Container(
            content=ft.Column([
                ft.Row([add_name, add_qty, add_unit, add_cost] if not mobile else [add_name, add_qty, add_unit, add_cost], spacing=6,
                       wrap=mobile),
                ft.Row([
                    self._btn("Save", ft.Icons.SAVE_ROUNDED,
                              lambda e: asyncio.create_task(do_save_add(e))),
                    self._btn("Cancel", ft.Icons.CLOSE_ROUNDED, lambda e: do_toggle_add(e)),
                ], alignment=ft.MainAxisAlignment.END),
            ], spacing=8),
            visible=False, margin=ft.Margin.only(bottom=6),
        )

        async def refresh():
            await self._render_ingredients(ref)

        def do_toggle_add(e):
            add_form.visible = not add_form.visible
            if not add_form.visible:
                add_name.value = add_qty.value = add_unit.value = add_cost.value = ""
            self.page.update()

        async def do_save_add(e):
            try:
                data = {
                    "Name": add_name.value.strip(),
                    "Total_Quantity": float(add_qty.value or 0),
                    "Unit": add_unit.value.strip(),
                    "Unit_cost": float(add_cost.value or 0),
                }
            except ValueError:
                self._snack("Invalid number", False); return
            if not data["Name"] or not data["Unit"]:
                self._snack("Name and Unit required", False); return
            if self.is_guest:
                mock_data.create_ingredient(data)
                self._snack("Created")
                await refresh()
            else:
                r = await _api("ingredients")["create"](self.email, data)
                if "error" in (r or {}): logger.error("create_ingredient: %s", r["error"]); self._snack(r["error"], False); return
                self._snack("Created"); await refresh()

        header = ft.Container(
            ft.Row([
                ft.Text("Name", size=11, weight="bold", color=self._clr("sub"), font_family="DM Sans", expand=True),
                ft.Text("Qty", size=11, weight="bold", color=self._clr("sub"), font_family="DM Sans", width=70, text_align=ft.TextAlign.CENTER),
                ft.Text("Unit", size=11, weight="bold", color=self._clr("sub"), font_family="DM Sans", width=60, text_align=ft.TextAlign.CENTER),
                ft.Text("Cost/Unit", size=11, weight="bold", color=self._clr("sub"), font_family="DM Sans", width=90, text_align=ft.TextAlign.CENTER),
                ft.Container(width=72),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self._clr("card"), border_radius=12,
            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
            margin=ft.Margin.only(bottom=4),
            visible=not self._is_mobile(),
        )

        for item in items:
            iid = item.get("Ingredient_ID")
            name = item.get("Name", "")
            qty = item.get("Total_Quantity", 0)
            unit = item.get("Unit", "")
            cost = item.get("Unit_cost", 0)
            label = f"{name} | {iid}"

            ef_name = ft.TextField(value=name, expand=True, dense=True,
                border_color=self._clr("accent"), border_radius=8,
                text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
                filled=True, fill_color=self._clr("card"),)
            ef_qty  = ft.TextField(value=str(qty), expand=mobile, width=70 if not mobile else None, dense=True,
                border_color=self._clr("accent"), border_radius=8,
                text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
                text_align=ft.TextAlign.CENTER, filled=True, fill_color=self._clr("card"),)
            ef_unit = ft.TextField(value=unit, expand=mobile, width=60 if not mobile else None, dense=True,
                border_color=self._clr("accent"), border_radius=8,
                text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
                text_align=ft.TextAlign.CENTER, filled=True, fill_color=self._clr("card"),)
            ef_cost = ft.TextField(value=str(cost), expand=mobile, width=90 if not mobile else None, dense=True,
                border_color=self._clr("accent"), border_radius=8,
                text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
                text_align=ft.TextAlign.CENTER, filled=True, fill_color=self._clr("card"),)

            def do_upd(e, i=iid, nf=ef_name, qf=ef_qty, uf=ef_unit, cf=ef_cost):
                try:
                    d = {"Name": nf.value, "Total_Quantity": float(qf.value or 0),
                         "Unit": uf.value, "Unit_cost": float(cf.value or 0)}
                except ValueError:
                    self._snack("Invalid number", False); return
                if self.is_guest:
                    mock_data.update_ingredient(i, d)
                    self._snack("Updated")
                else:
                    self._run(_upd_ing(i, d))
            async def _upd_ing(i=iid, d=None):
                r = await _api("ingredients")["update"](self.email, i, d)
                if "error" in (r or {}): logger.error("upd_ing %s: %s", i, r["error"]); self._snack(r["error"], False); return
                self._snack("Updated")

            def do_del(e, i=iid):
                if self.is_guest:
                    mock_data.delete_ingredient(i)
                    self._snack("Deleted")
                    asyncio.create_task(refresh())
                else:
                    self._confirm("Delete Ingredient", f"Remove {name}?", lambda: self._run(_del_ing(i)))
            async def _del_ing(i=iid):
                r = await _api("ingredients")["delete"](self.email, i)
                if "error" in (r or {}): logger.error("del_ing %s: %s", i, r["error"]); self._snack(r["error"], False); return
                self._snack("Deleted"); await refresh()

            if mobile:
                ing_rows.controls.append(ft.Container(
                    content=ft.Column([
                        ef_name,
                        ft.Row([ef_qty, ef_unit, ef_cost], spacing=6),
                        ft.Row([
                            self._icon_btn(ft.Icons.SAVE_ROUNDED, self._clr("accent"), "Save", do_upd),
                            self._icon_btn(ft.Icons.DELETE_ROUNDED, self._clr("danger"), "Delete", do_del),
                        ], alignment=ft.MainAxisAlignment.END),
                    ], spacing=6),
                    bgcolor=self._clr("card"), border_radius=12,
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    margin=ft.Margin.only(bottom=6),
                    data=label,
                ))
            else:
                ing_rows.controls.append(self._row_card([
                    ef_name, ef_qty, ef_unit, ef_cost,
                ], actions=[
                self._icon_btn(ft.Icons.SAVE_ROUNDED, self._clr("accent"), "Save", do_upd),
                self._icon_btn(ft.Icons.DELETE_ROUNDED, self._clr("danger"), "Delete", do_del),
            ], data=label))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([
                ft.Text("Ingredients", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                self._btn("Add Ingredient", ft.Icons.ADD_ROUNDED, do_toggle_add),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Row([search_bar], spacing=8),
            add_form,
            header,
            ing_rows if ing_rows.controls else ft.Text("No ingredients", color=self._clr("sub"), font_family="DM Sans"),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 5 — MESS OFF
    # ════════════════════════════════════════════════════════════

    async def _render_mess_off(self, ref):
        ref.content = self._loading(); self.page.update()
        if self.is_guest:
            requests = mock_data.get_mess_off_history().get("status", [])
        else:
            result = await _api("mess_off")["history"](self.email)
            requests = result.get("status", []) if isinstance(result, dict) else (result if isinstance(result, list) else [])

        s_colors = {"Approved": (self._clr("success"), ft.Colors.with_opacity(0.12, self._clr("success"))),
                    "Pending": (self._clr("warn"), ft.Colors.with_opacity(0.12, self._clr("warn"))),
                    "Rejected": (self._clr("danger"), ft.Colors.with_opacity(0.12, self._clr("danger"))),
                    "Cancelled": (self._clr("sub"), self._clr("card2"))}
        rows = []
        for req in requests:
            rid = req.get("Mess_Off_ID")
            status = req.get("Status", "Pending")
            fg, bg = s_colors.get(status, (self._clr("sub"), self._clr("card2")))
            acts = []
            if status == "Pending":
                def do_app(e, r=rid):
                    if self.is_guest:
                        mock_data.approve_mess_off(r)
                        self._snack("Approved")
                        asyncio.create_task(self._render_mess_off(ref))
                    else:
                        self._run(_app_off(r))
                async def _app_off(r=rid):
                    res = await _api("mess_off")["approve"](self.email, r)
                    if "error" in (res or {}): logger.error("app_off %s: %s", r, res["error"]); self._snack(res["error"], False); return
                    self._snack("Approved"); await self._render_mess_off(ref)
                def do_rej(e, r=rid):
                    if self.is_guest:
                        mock_data.reject_mess_off(r)
                        self._snack("Rejected")
                        asyncio.create_task(self._render_mess_off(ref))
                    else:
                        self._confirm("Reject Request", "Reject this mess-off request?", lambda: self._run(_rej_off(r)))
                async def _rej_off(r=rid):
                    res = await _api("mess_off")["reject"](self.email, r)
                    if "error" in (res or {}): logger.error("rej_off %s: %s", r, res["error"]); self._snack(res["error"], False); return
                    self._snack("Rejected"); await self._render_mess_off(ref)
                acts = [self._icon_btn(ft.Icons.CHECK_CIRCLE_ROUNDED, self._clr("success"), "Approve", do_app),
                        self._icon_btn(ft.Icons.CANCEL_ROUNDED, self._clr("danger"), "Reject", do_rej)]
            rows.append(self._row_card([
                ft.Column([
                    ft.Text(f"User #{req.get('User_ID','?')} \u2022 {req.get('Start_Date','?')} \u2192 {req.get('End_Date','?')}",
                            size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(f"ID #{rid} \u2022 {req.get('Request_Date','')}",
                            size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._chip(status, fg, bg),
            ], actions=acts))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Mess-Off Requests", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else ft.Text("No requests", color=self._clr("sub")),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 5 — BILLS
    # ════════════════════════════════════════════════════════════

    async def _render_bills(self, ref):
        ref.content = self._loading(); self.page.update()
        bills = (await _api("bills")["all"](self.email)) if not self.is_guest else mock_data.get_monthly_bills()

        def do_export(e):
            if self.is_guest:
                self._snack("Export not available in guest mode", ok=False); return
            asyncio.create_task(_export())

        async def _export():
            url = f"{BASE_URL}/admin/bills/export-csv?email={self.email}"
            try:
                await self.page.launch_url(url)
                self._snack("CSV download started")
            except Exception as ex:
                self._snack(f"Export failed: {ex}", ok=False)

        def do_generate(e):
            asyncio.create_task(_generate())

        async def _generate():
            r = await _api("bills")["generate"](self.email, 5000)
            if "error" not in (r or {}):
                self._snack(r.get("message", "Bills generated"))
                await self._render_bills(ref)
            else:
                self._snack(r.get("error", "Generation failed"), False)

        s_colors = {"Paid": (self._clr("success"), ft.Colors.with_opacity(0.12, self._clr("success"))),
                    "Unpaid": (self._clr("warn"), ft.Colors.with_opacity(0.12, self._clr("warn"))),
                    "Overdue": (self._clr("danger"), ft.Colors.with_opacity(0.12, self._clr("danger")))}
        rows = []

        async def refresh():
            await self._render_bills(ref)

        for b in (bills if isinstance(bills, list) else []):
            bid = b.get("Billing_ID")
            uid = b.get("User_ID")
            month = b.get("Month", "?")
            total = b.get("Amount", b.get("Total_Amount", 0))
            paid = b.get("Total_Collected", 0)
            outstanding = total - paid
            status = "Paid" if outstanding <= 0 else "Unpaid"
            fg, bg = s_colors.get(status, (self._clr("sub"), self._clr("card2")))

            ef_total = ft.TextField(value=str(round(total, 1)), dense=True, width=100,
                border_color=self._clr("accent"), border_radius=8,
                text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
                filled=True, fill_color=self._clr("card"))
            def do_save(e, b=bid, tf=ef_total):
                try:
                    amt = float(tf.value or 0)
                except ValueError:
                    self._snack("Invalid amount", False); return
                if self.is_guest:
                    mock_data.update_bill(b, {"Amount": amt, "Total_Amount": amt})
                    self._snack("Updated")
                    asyncio.create_task(refresh())
                else:
                    self._run(_save_bill(b, amt))
            async def _save_bill(b=bid, amt=0):
                r = await _api("bills")["update"](self.email, b, {"Amount": amt})
                if "error" in (r or {}): logger.error("save_bill %s: %s", b, r["error"]); self._snack(r["error"], False); return
                self._snack("Updated"); await refresh()
            def do_pay(e, b=bid, tf=ef_total, p=paid):
                try:
                    amt = float(tf.value or 0) - p
                    if amt <= 0: self._snack("Already paid", False); return
                except ValueError:
                    self._snack("Invalid amount", False); return
                if self.is_guest:
                    mock_data.pay_bill(b, amt)
                    self._snack("Paid")
                    asyncio.create_task(refresh())
                else:
                    self._run(_pay_bill(b, amt))
            async def _pay_bill(b=bid, amt=0):
                r = await _api("bills")["pay"](self.email, b, amt, "Cash")
                if "error" in (r or {}): logger.error("pay_bill %s: %s", b, r["error"]); self._snack(r["error"], False); return
                self._snack("Paid"); await refresh()

            name = b.get("First_Name", "")
            name_str = f" \u2022 {name}" if name else ""
            rows.append(self._row_card([
                ft.Column([
                    ft.Text(f"Bill #{bid}{name_str}", size=13, weight="bold",
                            color=self._clr("text"), font_family="DM Sans"),
                    ft.Row([
                        ft.Text("Amount:", size=11, color=self._clr("sub"), font_family="DM Sans"),
                        ef_total,
                    ], spacing=6),
                    ft.Text(f"Paid: PKR {paid:.0f} \u2022 Due: PKR {outstanding:.0f}",
                            size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._chip(status, fg, bg),
            ], actions=[
                self._icon_btn(ft.Icons.SAVE_ROUNDED, self._clr("accent"), "Save", do_save),
                self._icon_btn(ft.Icons.CHECK_CIRCLE_ROUNDED, self._clr("success"), "Mark Paid", do_pay),
            ]))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Bills", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Row([
                self._btn("Export CSV", ft.Icons.DOWNLOAD_ROUNDED, do_export),
                self._btn("Generate Monthly", ft.Icons.AUTO_GRAPH_ROUNDED, do_generate),
            ], spacing=8),
            ft.Container(height=8),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else ft.Text("No billing data", color=self._clr("sub")),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 6 — MENU
    # ════════════════════════════════════════════════════════════

    async def _render_menu(self, ref):
        ref.content = self._loading(); self.page.update()
        items = mock_data.get_weekly_menu() if self.is_guest else (await _api("menu")["weekly"](self.email)) or []

        m_colors = {"Breakfast": self._clr("warn"), "Lunch": self._clr("success"), "Dinner": self._clr("accent2")}
        rows = []
        for item in items:
            iid = item.get("Item_ID")
            sid = item.get("Schedule_ID")
            name = item.get("Name") or item.get("Food_Item_Name", "?")
            mt = item.get("meal_type", "")
            d = item.get("Date", "")
            mc = m_colors.get(mt, self._clr("accent"))
            def do_del(e, i=iid, s=sid):
                if self.is_guest:
                    mock_data.delete_menu_item(i, s)
                    self._snack("Removed")
                    asyncio.create_task(self._render_menu(ref))
                else:
                    self._confirm("Remove Menu Item", f"Remove {name}?", lambda: self._run(_del_menu(i, s)))
            async def _del_menu(i=iid, s=sid):
                r = await _api("menu")["delete"](self.email, i, s)
                if "error" in (r or {}): logger.error("del_menu %s/%s: %s", i, s, r["error"]); self._snack(r["error"], False); return
                self._snack("Removed"); await self._render_menu(ref)
            rows.append(self._row_card([
                ft.Container(
                    content=ft.Text(mt[:1], size=12, weight="bold", color=mc),
                    width=30, height=30, bgcolor=ft.Colors.with_opacity(0.12, mc),
                    border_radius=8, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(name, size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(f"{d} \u2022 {mt}", size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._icon_btn(ft.Icons.REMOVE_CIRCLE_ROUNDED, self._clr("danger"), "Remove", do_del),
            ]))

        # ── add menu form ──────────────────────────────────────
        add_m_date = ft.TextField(
            label="Date", hint_text="YYYY-MM-DD",
            value=date.today().isoformat(),
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")), border_radius=8,
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            filled=True, fill_color=self._clr("card"), expand=2,
        )
        add_m_meal = ft.Dropdown(
            options=[ft.dropdown.Option("Breakfast"), ft.dropdown.Option("Lunch"),
                     ft.dropdown.Option("Dinner")],
            value="Lunch",
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")), border_radius=8,
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            filled=True, fill_color=self._clr("card"), expand=1,
        )
        add_m_food = ft.Dropdown(
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")), border_radius=8,
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            filled=True, fill_color=self._clr("card"), expand=3,
        )

        # populate food dropdown
        all_food = (mock_data.get_food_costs() if self.is_guest
                    else (await _api("food")["all"](self.email)) or [])
        for fi in all_food:
            add_m_food.options.append(
                ft.dropdown.Option(key=str(fi.get("Item_ID")),
                                   text=f"{fi.get('Name', '?')} (PKR {fi.get('Price', 0):.0f})")
            )

        add_m_form = ft.Container(
            content=ft.Column([
                ft.Row([add_m_date, add_m_meal, add_m_food], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([
                    self._btn("Add to Menu", ft.Icons.ADD_ROUNDED,
                              lambda e: asyncio.create_task(do_add_menu(e))),
                ], alignment=ft.MainAxisAlignment.END),
            ], spacing=8),
            visible=False, margin=ft.Margin.only(bottom=6),
        )

        def do_toggle_add_m(e):
            add_m_form.visible = not add_m_form.visible
            self.page.update()

        async def do_add_menu(e):
            iid = add_m_food.value
            d = add_m_date.value.strip()
            t = add_m_meal.value
            if not iid or not d or not t:
                self._snack("All fields required", False); return
            if self.is_guest:
                mock_data.add_menu_item(iid, d, t)
                self._snack("Added")
                await self._render_menu(ref)
            else:
                r = await _api("menu")["add"](self.email, iid, d, t)
                if "error" in (r or {}): logger.error("add_menu: %s", r["error"]); self._snack(r["error"], False); return
                self._snack("Added"); await self._render_menu(ref)

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([
                ft.Text("Menu", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                self._btn("Add Item", ft.Icons.ADD_ROUNDED, do_toggle_add_m),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            add_m_form,
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else ft.Text("No menu items", color=self._clr("sub")),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 7 — POLLS
    # ════════════════════════════════════════════════════════════

    async def _render_polls(self, ref):
        ref.content = self._loading(); self.page.update()

        active_poll = (mock_data.get_active_poll() if self.is_guest
                       else await _api("poll")["active"](self.email))
        results = (mock_data.get_poll_results() if self.is_guest
                   else await _api("poll")["results"](self.email))
        poll_results = results.get("results", []) if isinstance(results, dict) else []

        selected_items = []
        search_rows = ft.Column(spacing=4)

        async def refresh():
            await self._render_polls(ref)

        # ── search food ────────────────────────────────────────
        async def do_search(q):
            search_rows.controls.clear()
            if not q or len(q.strip()) < 1:
                self.page.update(); return
            q = q.strip()
            if self.is_guest:
                sdata = mock_data.search_food(q)
            else:
                sdata = await _api("food")["search"](self.email, q)
                if isinstance(sdata, dict) and "error" in sdata:
                    logger.error("search failed: %s", sdata["error"])
                    sdata = []
            for fi in sdata:
                fid = fi.get("Item_ID")
                fname = fi.get("Name", "")
                fprice = fi.get("Price", 0)
                already = any(s.get("Item_ID") == fid for s in selected_items)
                search_rows.controls.append(self._row_card([
                    ft.Text(fname, expand=True, size=13, weight="bold",
                            color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(f"PKR {fprice:.0f}", size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], actions=[
                    self._icon_btn(
                        ft.Icons.ADD_CIRCLE_ROUNDED if not already else ft.Icons.CHECK_CIRCLE_ROUNDED,
                        self._clr("success") if not already else self._clr("sub"),
                        "Add" if not already else "Added",
                        lambda e, fi=fi: do_add(fi),
                    ),
                ]))
            if not sdata:
                search_rows.controls.append(ft.Text("No results", color=self._clr("sub"), font_family="DM Sans"))
            search_rows.update()
            self.page.update()

        # ── add to selected ────────────────────────────────────
        selected_view = ft.Column(spacing=4)

        def rebuild_selected():
            selected_view.controls.clear()
            for si in selected_items:
                sid = si.get("Item_ID")
                sname = si.get("Name", "")
                selected_view.controls.append(self._row_card([
                    ft.Text(sname, expand=True, size=13, weight="bold",
                            color=self._clr("text"), font_family="DM Sans"),
                    self._icon_btn(ft.Icons.REMOVE_CIRCLE_ROUNDED, self._clr("danger"), "Remove",
                                   lambda e, i=sid: do_remove(i)),
                ]))
            self.page.update()

        def do_add(fi):
            if not any(s.get("Item_ID") == fi.get("Item_ID") for s in selected_items):
                selected_items.append(fi)
                rebuild_selected()

        def do_remove(iid):
            nonlocal selected_items
            selected_items = [s for s in selected_items if s.get("Item_ID") != iid]
            rebuild_selected()

        # ── start poll ─────────────────────────────────────────
        meal_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option("Breakfast"), ft.dropdown.Option("Lunch"),
                     ft.dropdown.Option("Dinner")],
            value="Lunch", width=160,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")),
            border_radius=10, filled=True, fill_color=self._clr("card2"),
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
        )

        search_field = ft.TextField(
            hint_text="Search food to add\u2026", prefix_icon=ft.Icons.SEARCH_ROUNDED,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")),
            border_radius=10, filled=True, fill_color=self._clr("card2"),
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            on_change=lambda e: asyncio.create_task(do_search(e.control.value)),
            expand=True,
        )

        def do_start(e):
            if not selected_items:
                self._snack("Select at least one food item", False); return
            ids = [s.get("Item_ID") for s in selected_items]
            mt = meal_dropdown.value or "Lunch"
            if self.is_guest:
                mock_data.start_poll({"item_ids": ids, "meal_type": mt})
                self._snack("Poll started!")
                asyncio.create_task(refresh())
            else:
                self._run(_start_poll(ids, mt))
        async def _start_poll(ids, mt):
            r = await _api("poll")["start"](self.email, {"item_ids": ids, "meal_type": mt})
            if "error" in (r or {}): logger.error("start_poll: %s", r["error"]); self._snack(r["error"], False); return
            self._snack("Poll started!"); await refresh()

        # ── end poll ───────────────────────────────────────────
        def do_end(e):
            if self.is_guest:
                mock_data.end_poll()
                self._snack("Poll ended")
                asyncio.create_task(refresh())
            else:
                self._confirm("End Poll", "End the current poll?", lambda: self._run(_end_poll()))
        async def _end_poll():
            r = await _api("poll")["end"](self.email)
            if "error" in (r or {}): logger.error("end_poll: %s", r["error"]); self._snack(r["error"], False); return
            self._snack("Poll ended"); await refresh()

        # ── build sections ─────────────────────────────────────
        is_active = isinstance(active_poll, dict) and active_poll.get("active", False)

        active_section = ft.Container()
        if is_active:
            mt = active_poll.get("meal_type", "Poll")
            items_names = ", ".join(i.get("Name", "?") for i in active_poll.get("items", []))
            active_section = self._card(
                ft.Row([
                    ft.Icon(ft.Icons.HOW_TO_VOTE_ROUNDED, size=20, color=self._clr("success")),
                    ft.Text(f"Active Poll: {mt}", size=15, weight="bold",
                            color=self._clr("text"), font_family="DM Sans"),
                ], spacing=8),
                ft.Text(f"Items: {items_names}", size=12, color=self._clr("sub"), font_family="DM Sans"),
                ft.Row([self._btn("End Poll", ft.Icons.STOP_ROUNDED, do_end)], alignment=ft.MainAxisAlignment.END),
            )

        create_section = ft.Container()
        if not is_active:
            create_section = self._card(
                ft.Text("Start New Poll", size=15, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                ft.Row([ft.Text("Meal Type:", size=12, color=self._clr("sub"), font_family="DM Sans"), meal_dropdown], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                search_field,
                ft.Container(content=ft.Column([
                    ft.Text("Search Results", size=12, weight="bold", color=self._clr("sub"), font_family="DM Sans"),
                    search_rows,
                ]), margin=ft.Margin.only(top=4)),
                ft.Container(content=ft.Column([
                    ft.Row([ft.Text("Selected Items", size=12, weight="bold", color=self._clr("sub"), font_family="DM Sans"),
                            ft.Text(f"({len(selected_items)})", size=11, color=self._clr("accent"), font_family="DM Sans")], spacing=4),
                    selected_view,
                ]), margin=ft.Margin.only(top=8)),
                ft.Row([self._btn("Start Poll", ft.Icons.PLAY_ARROW_ROUNDED, do_start)], alignment=ft.MainAxisAlignment.END),
            )

        result_cards = [self._row_card([
            ft.Text(r.get("Name", "?"), expand=True, weight="bold",
                    color=self._clr("text"), font_family="DM Sans"),
            ft.Text(f"{r.get('Vote_Count', 0)} Votes", color=self._clr("accent"),
                    weight="bold", font_family="DM Sans"),
        ]) for r in poll_results]

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Polls", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            active_section,
            ft.Container(height=8) if is_active else ft.Container(),
            create_section,
            ft.Container(height=12),
            ft.Text("Results", size=14, weight="bold", color=self._clr("text"), font_family="DM Sans"),
            ft.Column(result_cards) if result_cards else ft.Text("No results yet", color=self._clr("sub"), font_family="DM Sans"),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 8 — REGISTRATION REQUESTS
    # ════════════════════════════════════════════════════════════

    async def _render_requests(self, ref):
        ref.content = self._loading(); self.page.update()
        requests = mock_data.get_registration_requests() if self.is_guest else (await _api("registration")["list"](self.email, "Pending")) or []

        s_colors = {"Pending": (self._clr("warn"), ft.Colors.with_opacity(0.12, self._clr("warn"))),
                    "Approved": (self._clr("success"), ft.Colors.with_opacity(0.12, self._clr("success"))),
                    "Rejected": (self._clr("danger"), ft.Colors.with_opacity(0.12, self._clr("danger")))}
        cards = []
        for r in requests:
            rid = r.get("RequestID")
            name = f"{r.get('First_Name','')} {r.get('Last_Name','')}"
            role = r.get("Account_Type", "")
            email = r.get("Email", "")
            info = f"{role} \u2022 {email}" + (f" \u2022 {r.get('Department','')} \u2022 {r.get('Hostel_Name','')}" if role == "Student" else f" \u2022 {r.get('Category','')}")
            status = r.get("Status", "Pending")
            fg, bg = s_colors.get(status, (self._clr("sub"), self._clr("card2")))
            acts = []
            if status == "Pending":
                def do_app(e, ri=rid):
                    if self.is_guest:
                        mock_data.approve_registration(ri)
                        self._snack("Approved")
                        asyncio.create_task(self._render_requests(ref))
                    else:
                        self._run(_app_reg(ri))
                async def _app_reg(ri=rid):
                    rr = await _api("registration")["approve"](self.email, ri, None)
                    if "error" in (rr or {}): logger.error("app_reg %s: %s", ri, rr["error"]); self._snack(rr["error"], False); return
                    self._snack("Approved"); await self._render_requests(ref)
                def do_rej(e, ri=rid):
                    if self.is_guest:
                        mock_data.reject_registration(ri)
                        self._snack("Rejected")
                        asyncio.create_task(self._render_requests(ref))
                    else:
                        self._confirm("Reject Request", f"Reject {name}'s registration?", lambda: self._run(_rej_reg(ri)))
                async def _rej_reg(ri=rid):
                    rr = await _api("registration")["reject"](self.email, ri)
                    if "error" in (rr or {}): logger.error("rej_reg %s: %s", ri, rr["error"]); self._snack(rr["error"], False); return
                    self._snack("Rejected"); await self._render_requests(ref)
                acts = [self._icon_btn(ft.Icons.CHECK_CIRCLE_ROUNDED, self._clr("success"), "Approve", do_app),
                        self._icon_btn(ft.Icons.CANCEL_ROUNDED, self._clr("danger"), "Reject", do_rej)]
            cards.append(self._row_card([
                ft.Column([
                    ft.Text(name, size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(info, size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._chip(status, fg, bg),
            ], actions=acts))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Registration Requests", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Column(cards, scroll=ft.ScrollMode.ADAPTIVE) if cards else ft.Text("No pending requests", color=self._clr("sub")),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  BUILD
    # ════════════════════════════════════════════════════════════

    async def _safe_render(self, method_name, ref):
        try:
            await getattr(self, method_name)(ref)
        except Exception as e:
            logger.error("render %s failed: %s", method_name, e, exc_info=True)
            ref.content = ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, size=48, color=self._clr("danger")),
                ft.Text(f"Error: {e}", color=self._clr("danger"), font_family="DM Sans", size=14),
            ], alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()

    RENDERERS = [
        "_render_dashboard", "_render_students", "_render_staff",
        "_render_food", "_render_ingredients", "_render_mess_off",
        "_render_bills", "_render_menu", "_render_polls",
        "_render_requests",
    ]

    def build(self):
        mobile = self._is_mobile()

        def select_tab(idx):
            self.tab_idx["v"] = idx
            sidebar.controls[0] = self._sidebar(select_tab)
            self.content.opacity = 0
            self.page.update()
            async def _do():
                await asyncio.sleep(0.05)
                await self._safe_render(self.RENDERERS[idx], self.content)
                self.content.opacity = 1
                self.page.update()
            asyncio.create_task(_do())

        sidebar = ft.Column([self._sidebar(select_tab)])
        if mobile:
            layout = ft.Column([
                sidebar,
                ft.Container(content=self.content, expand=True,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8)),
            ], expand=True, spacing=6)
        else:
            layout = ft.Row([
                sidebar,
                ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, self._clr("text"))),
                ft.Container(content=self.content, expand=True,
                    padding=ft.Padding.symmetric(horizontal=20, vertical=8)),
            ], expand=True, spacing=0)

        asyncio.create_task(self._safe_render("_render_dashboard", self.content))

        hp = 12 if mobile else 20
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Admin", size=20 if mobile else 24, weight="bold",
                            font_family="DM Sans", color=self._clr("text")),
                    self._chip("Admin", self._clr("accent"), ft.Colors.with_opacity(0.12, self._clr("accent"))),
                ], spacing=12),
                ft.Container(height=4 if mobile else 8),
                ft.Container(content=layout, expand=True),
            ], expand=True),
            expand=True,
            padding=ft.Padding.symmetric(horizontal=hp, vertical=12 if mobile else 16),
        )
