const ARTIFACT_IMAGES = {
    "AV-1001": "/static/images/talwar.jpg",
    "AV-1002": "/static/images/bichwa.jpg",
    "AV-1003": "/static/images/chainmail.jpg",

    "AV-1004": "/static/images/shivrai_coin.jpg",
    "AV-1005": "/static/images/gold_mohur.jpg",
    "AV-1006": "/static/images/satavahana_coin.jpg",

    "AV-1007": "/static/images/raigad_fort.jpg",
    "AV-1008": "/static/images/sindhudurg_fort.jpg",
    "AV-1009": "/static/images/lohagad_fort.jpg",

    "AV-1010": "/static/images/dvarapala.jpg",
    "AV-1011": "/static/images/bronze_vithoba.jpg",

    "AV-1013": "/static/images/modi_letter.jpg",
    "AV-1014": "/static/images/sanskrit_manuscript.jpg",

    "AV-1015": "/static/images/paithani_saree.jpg",
    "AV-1016": "/static/images/nauvari_saree.jpg",
    "AV-1017": "/static/images/kolhapuri_pheta.jpg",

    "AV-1018": "/static/images/maratha_wall_hanging.jpg",
};

const CATEGORY_IMAGES = {
    "Weaponry": "/static/images/talwar.jpg",
    "Coins & Currency": "/static/images/shivrai_coin.jpg",
    "Fort Models": "/static/images/raigad_fort.jpg",
    "Temple Sculptures": "/static/images/dvarapala.jpg",
    "Manuscripts": "/static/images/modi_letter.jpg",
    "Costumes & Textiles": "/static/images/paithani_saree.jpg",
};

function getArtifactIllustration(artifact) {
    return (
        ARTIFACT_IMAGES[artifact.id] ||
        CATEGORY_IMAGES[artifact.category] ||
        "/static/images/no-image.png"
    );
}