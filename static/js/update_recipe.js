var ingredient_list = [];

// Remove ingredient
function remove_ingredient(num) {
    ingredient_list.splice(num, 1);
    display_ingredient();
}

function display_ingredient() {
    var ingredient_itemHTML = ""
    for (i = 0; i < ingredient_list.length; i++) {
        ingredient_itemHTML += '<div class="ingredient_item" id="' + ingredient_list[i] +  `" style="width:fit-content">
        <i class="bi bi-x remove_ingredient" id="remove_` + ingredient_list[i] + '" onclick="remove_ingredient(' + i + `)"></i>
        <span class="item">` + ingredient_list[i] + "</span></div>";
    }
    document.getElementById('ingredient_items_list').innerHTML = ingredient_itemHTML;

}

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
            var regex = /^[a-zA-Z ]+$/;
            if (regex.test(ingredient)) {
                if (ingredient_list.includes(ingredient)) {
                    display_popup('Ingredient is already added.' , 'error')
                }
                else {
                    ingredient_list.push(ingredient);
                    display_ingredient();
                }
            }
            else {
                display_popup('Letters and spaces are only accepted.' , 'error');
            }
        }
        display_ingredient();
    })
    const remove_all = document.getElementById('remove_all');
    remove_all.addEventListener('click', function() {
        ingredient_list = [];
        display_ingredient();
    })
})


// Checking inputs before submitting recipe
function submit_recipe1() { 
    recipe_name_input = document.getElementById('name').value;
    recipe_instruction_input = document.getElementById('instructions').value;
    var regex = /^[a-zA-Z\s]+$/;
    if (regex.test(recipe_name_input)) {
        if (recipe_name_input.trim() == '') {
            document.getElementById('name').value = ''
        }
        if (recipe_instruction_input.trim() == '') {
            document.getElementById('instructions').value = '';
        }



        document.getElementById('ingredients').value = ingredient_list;
        document.getElementById('create_recipe_form').submit();
    }
    else {
        display_popup('Letters are only accepted for the name.', 'error');
    }
}
    
  
  
  // Sending POST request
  function search_ingredients() {
      document.getElementById('ingredient').value = ingredient_list;
  }

function add_ingredient_item(string1) {
    ingredient_list.push(string1);
    display_ingredient;
}