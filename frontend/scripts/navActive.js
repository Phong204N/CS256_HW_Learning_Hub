let curr = window.location.href.split("/")
curr = curr[curr.length-1]

let tgt = null;
let expand = false;
switch (curr){
    case "home":
        tgt = document.getElementById("navHome");
        break;
    case "trending":
        tgt = document.getElementById("navTrends");
        break;
    case "chatbot":
        tgt = document.getElementById("navChatbot");
        break;
    case "profile":
        tgt = document.getElementById("navProfile");
        expand = true;
        break;
    case "my_resources":
        tgt = document.getElementById("navResources");
        expand = true;
        break;
    case "submit_resource":
        tgt = document.getElementById("navSubmit");
        expand = true;
        break;
    case "dashboard":
        tgt = document.getElementById("navAdmin");
        expand = true;
        break;
    case "my_bookmarks":
        tgt = document.getElementById("navBookmarks");
        expand = true;
        break;
    default:
        void(0);
}

tgt.setAttribute("aria-current", "page");
tgt.setAttribute("class", tgt.getAttribute("class") + " active")

if(expand){
    navDropdown = document.getElementById("navDropdown");
    navDropdown.setAttribute("aria-expanded", "true");
    navDropdown.setAttribute("class", navDropdown.getAttribute("class") + " show")
}