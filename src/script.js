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
    const selectBoxs = document.querySelectorAll('.select-box');
    selectBoxs.forEach(selectBox => selectBox.classList.remove('show'));
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
    // 删除所有的task-item
    const taskItems = document.querySelectorAll('.task-item');
    taskItems.forEach(taskItem => taskItem.parentNode.removeChild(taskItem));
    // 获取config中的数据
    const response = pywebview.api.get_config();
    const config = JSON.parse(response);
    if (config.users[account].hasOwnProperty('task')) {
        Object.keys(config.users[account].task).forEach(challenge => {
            Object.keys(config.users[account].task[challenge]).forEach(task => {
                const taskCount = config.users[account].task[challenge][task];
                const taskItem = document.createElement('div');
                taskItem.className = 'task-item';
                taskItem.innerHTML = `
                            <span class="name">${task}</span>
                            <div>
                                <button onclick="decrement(this)">-</button>
                                <span class="task-count">${taskCount}</span>
                                <button onclick="increment(this)">+</button>
                                <button onclick="removeTask(this, '${task}')">删除</button>
                            </div>
                        `;
                const challengePage = document.getElementById(challenge)
                const settingDiv = challengePage.querySelector('.setting');
                challengePage.insertBefore(taskItem, settingDiv);
            });
        }
        )
    }
}

async function addAccount() {
    // 弹出一个输入框，要求用户输入账号和密码
    const account = prompt('请输入账号');
    // 如果用户点击了取消按钮，则返回
    if (account) {
        const password = prompt('请输入密码');
        if (password) {
            // 将账号和密码写入config中
            const response = await pywebview.api.add_account(account, password);
            const changePage = document.getElementById('changepage');
            const contentItem = document.getElementById('new-account');
            const accountNum = document.createElement('div');
            accountNum.classList.add('account-num');
            accountNum.textContent = account;
            accountNum.onclick = changeAccount;
            changePage.insertBefore(accountNum, contentItem);
            document.querySelector('.add-account').style.display = 'none';
            document.querySelector('.show-account').style.display = 'flex';
            const sidebarItems = document.querySelectorAll('.sidebar-item');
            sidebarItems.forEach(item => item.style.display = 'flex');
            document.getElementById('userpage').style.display = 'flex';
            document.getElementById('changepage').style.display = 'none';
            // 获取 .account 元素
            const accountDiv = document.querySelector('.account');
            // 将 .account 元素的文本内容替换为 account 变量的值
            accountDiv.textContent = account;
            // 删除所有的task-item
            const taskItems = document.querySelectorAll('.task-item');
            taskItems.forEach(taskItem => taskItem.parentNode.removeChild(taskItem));
        };
    }
}

function addTask(pageName) {
    const contentPage = document.getElementById(pageName);
    const selectBox = contentPage.querySelector('.select-box');
    selectBox.classList.toggle('show');
}

function selectTask(taskName) {
    const selectBoxs = document.querySelectorAll('.select-box');
    selectBoxs.forEach(selectBox => selectBox.classList.remove('show'));
    const option = document.getElementById(taskName);
    option.style.display = 'none';

    const taskItem = document.createElement('div');
    taskItem.className = 'task-item';
    taskItem.innerHTML = `
                <span class="name">${taskName}</span>
                <div>
                    <button onclick="decrement(this)">-</button>
                    <span class="task-count">1</span>
                    <button onclick="increment(this)">+</button>
                    <button onclick="removeTask(this, '${taskName}')">删除</button>
                </div>
            `;

    const taskDiv = document.getElementById(taskName);
    // taskDiv的父元素的前一个兄弟元素
    const settingDiv = taskDiv.parentElement.previousElementSibling;
    settingDiv.parentNode.insertBefore(taskItem, settingDiv);
}

function decrement(button) {
    const countSpan = button.nextElementSibling;
    const count = parseInt(countSpan.textContent);
    if (count > 0) {
        countSpan.textContent = count - 1;
    }
}

function increment(button) {
    const countSpan = button.previousElementSibling;
    const count = parseInt(countSpan.textContent);
    countSpan.textContent = count + 1;
}

function removeTask(button, taskName) {
    const taskItem = button.parentNode.parentNode;
    taskItem.parentNode.removeChild(taskItem);

    const option = document.getElementById(taskName);
    option.style.display = 'block';
}

async function load_config() {
    const response = await pywebview.api.get_config();
    const config = JSON.parse(response);
    // 检查config是否包含users属性
    if (!config.hasOwnProperty('users')) {
        document.querySelector('.add-account').style.display = 'flex';
        return;
    }
    else {
        document.querySelector('.show-account').style.display = 'flex';
        const sidebarItems = document.querySelectorAll('.sidebar-item');
        sidebarItems.forEach(item => item.style.display = 'flex');
        document.getElementById('userpage').style.display = 'flex';
        // 获取 .account 元素
        const accountDiv = document.querySelector('.account');
        // 获取config中users中的第1组数据的key
        const accounts = Object.keys(config.users);
        const account = accounts[0];
        // 将 .account 元素的文本内容替换为 account 变量的值
        accountDiv.textContent = account;
        // 在.changepage中动态地为accounts中的每一个值创建一个<div class="account-num" onclick="changeAccount(event)"></div>，其中文本内容为对应的值
        const changePage = document.getElementById('changepage');
        const contentItem = document.getElementById('new-account');
        accounts.forEach(account => {
            const accountNum = document.createElement('div');
            accountNum.classList.add('account-num');
            accountNum.textContent = account;
            accountNum.onclick = changeAccount;
            changePage.insertBefore(accountNum, contentItem);
        });
        if (config.users[account].hasOwnProperty('task')) {
            Object.keys(config.users[account].task).forEach(challenge => {
                Object.keys(config.users[account].task[challenge]).forEach(task => {
                    const taskCount = config.users[account].task[challenge][task];
                    const taskItem = document.createElement('div');
                    taskItem.className = 'task-item';
                    taskItem.innerHTML = `
                                <span class="name">${task}</span>
                                <div>
                                    <button onclick="decrement(this)">-</button>
                                    <span class="task-count">${taskCount}</span>
                                    <button onclick="increment(this)">+</button>
                                    <button onclick="removeTask(this, '${task}')">删除</button>
                                </div>
                            `;
                    const challengePage = document.getElementById(challenge)
                    const settingDiv = challengePage.querySelector('.setting');
                    challengePage.insertBefore(taskItem, settingDiv);
                });
            }
            )
        }
    }
}

window.onload = function () {
    setTimeout(load_config, 500);
}

async function confirm(div) {
    const tasks = {};
    const account = document.querySelector('.account').textContent;
    const challengeName = div.parentNode.parentNode.id;
    const taskItems = div.parentNode.parentNode.querySelectorAll('.task-item');
    taskItems.forEach(taskItem => {
        const taskName = taskItem.querySelector('.name').textContent;
        const taskCount = parseInt(taskItem.querySelector('.task-count').textContent);
        tasks[taskName] = taskCount;
    });
    await pywebview.api.setting_tasks(account, challengeName, tasks);
    // 创建并显示保存成功的消息
    const messageDiv = document.createElement('div');
    messageDiv.textContent = "保存成功";
    messageDiv.style.position = 'fixed';
    messageDiv.style.bottom = '10px';
    messageDiv.style.left = '50%';
    messageDiv.style.transform = 'translateX(-50%)';
    messageDiv.style.backgroundColor = 'green';
    messageDiv.style.color = 'white';
    messageDiv.style.padding = '10px';
    messageDiv.style.borderRadius = '5px';
    document.body.appendChild(messageDiv);

    // 3秒后移除消息
    setTimeout(() => {
        document.body.removeChild(messageDiv);
    }, 3000);
}

async function start() {
    await pywebview.api.start();

}