<script>
  function toggleMenu(menuId) {
    const menu = document.getElementById(menuId);
    const toggleIcon = menu.previousElementSibling.querySelector('.menu-toggle');

    if (menu.classList.contains('active')) {
      menu.classList.remove('active');
      toggleIcon.classList.remove('active');
    } else {
      // Close any other open dropdowns
      document.querySelectorAll('.dropdown-menu').forEach(item => item.classList.remove('active'));
      document.querySelectorAll('.menu-toggle').forEach(item => item.classList.remove('active'));

      // Open the clicked dropdown
      menu.classList.add('active');
      toggleIcon.classList.add('active');
    }
  }
</script>
