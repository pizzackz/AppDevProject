// Confirmation button
function confirmdelete(content, id) {
    console.log(content);
    document.getElementById('modal-body').innerHTML = 'Are you sure you want to delete ' + content + '?';
    document.getElementById('delete').onclick = function() {
        window.location.href = "/delete_article/" + id;
    }
}