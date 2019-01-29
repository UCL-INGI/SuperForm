
var defaultFields = [
    {
        "id": "titlepost",
        "regex": /.*titlepost/
    },
    {
        "id": "descriptionpost",
        "regex": /.*descriptionpost/
    },
    {
        "id": "linkurlpost",
        "regex": /.*linkurlpost/
    },
    {
        "id": "imagepost",
        "regex": /.*imagepost/
    },
    {
        "id": "dateuntilpost",
        "regex": /.*dateuntilpost/
    },
    {
        "id": "datefrompost",
        "regex": /.*datefrompost/
    }
];

var selector = $("#js-tab-selector");
selector.find('input[type="checkbox"]').one("change", function() {
    if (this.checked) {
        var home = $(document).find("#home");
        var menu = $(document).find("#menu" + $(this).val());
        if ($(this).attr("data-new") == "True") {
            for (var k = 0; k < defaultFields.length; k++) {
                var text = home.find("#" + defaultFields[k].id).val();
                menu.find(".form-control").filter(function() {
                    return this.id.match(defaultFields[k].regex);
                }).val(text)
            }
        }
    }
});