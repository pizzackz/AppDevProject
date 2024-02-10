var ingredient_list = [];

// Loading document page
localStorageGet();
if (ingredient_list == null) {
    ingredient_list = [];
}

// Remove ingredient
function remove_ingredient(num) {
    ingredient_list.splice(num, 1);
    display_ingredient();
    localStorageStore();
}

// Display ingredient
function display_ingredient() {
    var ingredient_itemHTML = ""
    for (i = 0; i < ingredient_list.length; i++) {
        ingredient_itemHTML += '<div class="ingredient_item" id="' + ingredient_list[i] +  `" style="width:fit-content">
        <i class="bi bi-x remove_ingredient" id="remove_` + ingredient_list[i] + '" onclick="remove_ingredient(' + i + `)"></i>
        <span class="item">` + ingredient_list[i] + "</span></div>";
    }
    document.getElementById('ingredient_items_list').innerHTML = ingredient_itemHTML;
    
}

// Add event listeners to buttons
document.addEventListener("DOMContentLoaded", function() {
    const form1 = document.getElementById('form1');
    const add_item = document.getElementById("add_ingredient");
    display_ingredient();
    add_item.addEventListener('click', function() { // Add event listener to adding ingredient button
        var ingredient = document.getElementById('ingredient').value;
        ingredient = ingredient.toLowerCase();
        if (ingredient.trim() == '') {
            display_popup('The input is empty.', 'error')
        }
        else {
            var regex = /^[a-zA-Z\s]+$/;
            if (regex.test(ingredient)) {
                if (ingredient_list.includes(ingredient)) {
                    display_popup('Ingredient is already added.', 'error')
                }
                else {
                    ingredient_list.push(ingredient);
                    display_ingredient();
                    localStorageStore();
                }
            }
            else {
                display_popup('Letters are only accepted.', 'error');
            }
        }
        display_ingredient();
    })
    const remove_all = document.getElementById('remove_all');
    remove_all.addEventListener('click', function() {
        ingredient_list = [];
        display_ingredient();
        localStorageStore();
    })
    const search = document.getElementById('search');
    search.addEventListener('click', search_ingredients);
})

// Display popup

function hide_popup() {
    var popup = document.getElementById('popup');
    popup.classList.remove('show1');
    popup.classList.add('hide');
}




// Checking ingredient list before sending POST request 
function search_ingredients() {
    console.log(ingredient_list)
    if (ingredient_list.length == 0) {
        display_popup('Ingredient list is empty!', 'error');
    }
    else {
        document.getElementById('ingredient').value = ingredient_list;
        document.getElementById('form1').submit();
    }
    
}
// Local Storage
function localStorageStore() {
    const jsonString = JSON.stringify(ingredient_list);
    const key = "ArrayData";
    localStorage.setItem(key,jsonString); 
}
function localStorageGet() {
    const key = "ArrayData";
    const jsonString = localStorage.getItem(key);
    ingredient_list = JSON.parse(jsonString);
}

// Activate overlay
function overlayon() {
    const overlay = document.getElementById('overlay');
    overlay.style.display = 'block';
}
function overlayoff() {
    const overlay = document.getElementById('overlay');
    overlay.style.display = 'none';
}


