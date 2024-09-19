{
    "name": "Real Estate App",
    "summary": "Test Module",
    "version": "17.0.0.0.0",
    "license": "OEEL-1",
    "installable":True,
    "application":True,
    "depends": ["crm"],
    "sequence":-1000,
    "data": [
        #SECURITY
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        #VIEWS
        "views/estate_actions.xml",
        "views/estate_property_views.xml",
        "views/estate_menus.xml",
        #MENUS
    ],
    "demo": [
        "demo/demo.xml"
    ]
}