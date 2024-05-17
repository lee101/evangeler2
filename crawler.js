let $table = $("#app main div.relative.overflow-x-auto > table");

let data = [];
let storedData = localStorage.getItem("data");
if (storedData) {
    data = JSON.parse(storedData);
}
let index = 0;

let $el = $table;
while (true) {

    const brandNode = $el.querySelector("tr:nth-child(" + (index + 1) + ") > td:nth-child(1) > div > div:nth-child(2) > a");
    let brand = brandNode?.textContent;
    let imageUrl = $el.querySelector("tr:nth-child(" + (index + 1) + ") > td:nth-child(1) > div > div.flex-shrink-0.w-10.h-10 > img")?.getAttribute("src");

    const descriptionNode = $el.querySelector("tr:nth-child(" + (index + 1) + ") > td:nth-child(2)");
    let description = descriptionNode ? descriptionNode.textContent : '';

    let website = $el.querySelector("tr:nth-child(" + (index + 1) + ") > td:nth-child(3) > a")?.textContent;
    let keywords = Array.from($el.querySelectorAll("tr:nth-child(" + (index + 1) + ") > td:nth-child(4) > div")).filter(el => el);
    keywords = keywords.map(el => el ? el.textContent: '');
    keywords = keywords.filter(keyword => keyword !== '');
    

    if (!brand || !imageUrl || !description || !website || !keywords || keywords.includes(null)) {
        break;
    }
    data.push({
        brand: brand,
        imageUrl: imageUrl,
        description: description,
        website: website,
        keywords: keywords.join(", ")
    });
    index++;
}
console.log(data);
localStorage.setItem("data", JSON.stringify(data));