{
    "name": "Imprest Application",
    "summary": "Money Enquiry Aid",
    "version": "17.0.0.0.0",
    "license": "OEEL-1",
    "installable":True,
    "application":True,
    "sequence": -999,
    "data":[
        #SECURITY
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        #VIEWS
        "views/imprest_app_views.xml",
        #ACTIONS
        "views/imprest_app_actions.xml",
        #MENUS
        "views/imprest_app_menus.xml"
    ]

}
