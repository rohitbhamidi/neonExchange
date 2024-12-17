from dash import html
import dash_bootstrap_components as dbc

def sidebar(active_page=None):
    """
    Creates a sidebar navigation with icons and tooltips.
    active_page: a string representing the current page for highlighting.
    """
    nav_items = [
        {"label": "Real-time Trading", "href": "/realtime", "icon": "fas fa-chart-line"},
        {"label": "Analytics", "href": "/analytics", "icon": "fas fa-chart-bar"}
    ]

    def nav_link(item):
        active_class = "active" if active_page == item["href"] else ""
        return html.A(
            [
                html.I(className=item["icon"]),
                html.Span(item["label"], style={"marginLeft":"10px"})
            ],
            className=f"nav-link {active_class}",
            href=item["href"]
        )

    return html.Div(
        className="sidebar",
        children=[
            html.Div(
                [
                    html.H2("Dashboard", style={"color":"#FFFFFF","marginBottom":"30px","textAlign":"center","fontSize":"20px"})
                ]
            ),
            nav_link(nav_items[0]),
            nav_link(nav_items[1])
        ]
    )
