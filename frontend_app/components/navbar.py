from dash import html
import dash_bootstrap_components as dbc

def navbar():
    """
    Navbar component for navigation between pages.
    """
    nav_links = dbc.Nav(
        [
            dbc.NavLink("Real-time Trading", href="/realtime", active="exact", style={"color": "#FFFFFF"}),
            dbc.NavLink("Analytics", href="/analytics", active="exact", style={"color": "#FFFFFF"})
        ],
        navbar=True
    )

    brand = dbc.NavbarBrand("Stocks Dashboard", style={"color": "#FFFFFF"})
    navbar_content = dbc.Navbar(
        [
            brand,
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(nav_links, id="navbar-collapse", navbar=True)
        ],
        color="#333333",
        dark=True,
        style={"padding": "10px"}
    )
    return navbar_content
