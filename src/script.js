function showContent(contentId, event) {
    // Hide all content items
    const contents = document.querySelectorAll('.content-page');
    contents.forEach(content => content.style.display = 'none');
    // Show the selected content item
    document.getElementById(contentId).style.display = 'flex';
    // Remove active class from all sidebar items
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    sidebarItems.forEach(item => item.classList.remove('active'));
    // Add active class to the clicked sidebar item
    event.currentTarget.classList.add('active');
}

function changeAccount(event) {
    const account = event.currentTarget.textContent;
    // 获取 .account 元素
    const accountDiv = document.querySelector('.account');
    // 将 .account 元素的文本内容替换为 account 变量的值
    accountDiv.textContent = account;
    // Hide all content items
    const contents = document.querySelectorAll('.content-page');
    contents.forEach(content => content.style.display = 'none');
    // Show the selected content item
    document.getElementById("userpage").style.display = 'flex';
}