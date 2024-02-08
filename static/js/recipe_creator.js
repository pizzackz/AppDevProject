var ingredient_list = [];

// Loading document page
if (ingredient_list == null) {
    ingredient_list = [];
}

// Remove ingredient
function remove_ingredient(num) {
    ingredient_list.splice(num, 1);
    display_ingredient();
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
    })
})

// Display popup

function hide_popup() {
    var popup = document.getElementById('popup');
    popup.classList.remove('show1');
    popup.classList.add('hide');
}
// Checking inputs before submitting recipe
function submit_recipe1() { 
  recipe_name_input = document.getElementById('name').value;
  recipe_instruction_input = document.getElementById('instructions').value;
  file_input = document.getElementById('picture');
  file = file_input.files;

  if (file.length == 0) {
    display_popup('No file uploaded', 'error')
  }
  else {
    console.log(recipe_name_input, recipe_instruction_input);
    if (ingredient_list == []) {
      display_popup('Ingredient list is empty!', 'error')
    }
    var regex = /^[a-zA-Z\s]+$/;
    if (recipe_name_input.trim() == '') {
      display_popup('Empty inputs.', 'error')
    }
    else {
      if (recipe_instruction_input.trim() == '') {
        display_popup('Empty inputs.', 'error');
      }
      else {
        if (regex.test(recipe_name_input)) {
            document.getElementById('ingredients').value = ingredient_list;
            document.getElementById('create_recipe_form').submit();
        }
        else {
            display_popup('Letters are only accepted for the name.', 'error');
        }
      }
    }
  }
}


// Sending POST request
function search_ingredients() {
    document.getElementById('ingredient').value = ingredient_list;
}





