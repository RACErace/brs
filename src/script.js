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

async function changeAccount(account) {
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
    const response = await pywebview.api.get_config();
    const config = JSON.parse(response);
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
            const addTaskDiv = challengePage.querySelector('.add_task');
            challengePage.insertBefore(taskItem, addTaskDiv);
        });
    }
    )
    const dailyTraining = config.users[account].dailyTraining;
    const dailyTrainingSwitch = document.getElementById('dailyTrainingSwitch');
    dailyTrainingSwitch.checked = dailyTraining;
    const assignments = config.users[account].assignments;
    const assignmentsSwitch = document.getElementById('assignmentsSwitch');
    assignmentsSwitch.checked = assignments;

}

async function addAccount() {
    // 弹出一个输入框，要求用户输入账号和密码
    const account = prompt('请输入账号');
    // 如果用户点击了取消按钮，则返回
    if (account) {
        const password = prompt('请输入密码');
        if (password) {
            // 将账号和密码写入config中
            await pywebview.api.add_account(account, password);
            const changePage = document.getElementById('changepage');
            const contentItem = document.getElementById('new-account');
            const accountNum = document.createElement('div');
            accountNum.className = 'account-num';
            accountNum.id = account;
            accountNum.innerHTML = `
                <span>${account}</span>
                <div>
                    <button onclick="changeAccount(${account})">选择</button>
                    <button onclick="deleteAccount(${account})">删除</button>
                </div>
                `;
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
            const dailyTrainingSwitch = document.getElementById('dailyTrainingSwitch');
            dailyTrainingSwitch.checked = false;
            const assignmentsSwitch = document.getElementById('assignmentsSwitch');
            assignmentsSwitch.checked = false;
        };
    }
}

async function deleteAccount(account) {
    // 获取现在展示的账号号码
    const nowAccount = document.querySelector('.account').textContent;
    // 删除config中相应的账号信息
    await pywebview.api.delete_account(account);
    // 在.changepage中删除相应的账号
    const accountNum = document.getElementById(account);
    accountNum.parentNode.removeChild(accountNum);
    // 如果删除的账号是当前展示的账号，则将展示的账号切换为第一个账号，如果没有账号，则显示添加账号页面
    if (nowAccount == account) {
        console.log(nowAccount, account);
        const accountNums = document.querySelectorAll('.account-num');
        console.log(accountNums.length);
        if (accountNums.length > 1) {
            const newAccount = accountNums[0].id;
            changeAccount(newAccount);
        }
        else {
            document.querySelector('.add-account').style.display = 'flex';
            document.querySelector('.show-account').style.display = 'none';
            const sidebarItems = document.querySelectorAll('.sidebar-item');
            sidebarItems.forEach(item => item.style.display = 'none');
            document.getElementById('changepage').style.display = 'none';
        }
    }
}

function addTask(pageName) {
    const contentPage = document.getElementById(pageName);
    const selectBox = contentPage.querySelector('.select-box');
    selectBox.classList.toggle('show');
}

function selectTask(taskName) {
    const selectBox = document.getElementById(taskName).parentElement;
    selectBox.classList.remove('show');
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

    // select-box的前一个兄弟元素
    const addTaskDiv = selectBox.previousElementSibling;
    addTaskDiv.parentNode.insertBefore(taskItem, addTaskDiv);
    setting_tasks();
}

function decrement(button) {
    const countSpan = button.nextElementSibling;
    const count = parseInt(countSpan.textContent);
    if (count > 0) {
        countSpan.textContent = count - 1;
    }
    setting_tasks();
}

function increment(button) {
    const countSpan = button.previousElementSibling;
    const count = parseInt(countSpan.textContent);
    countSpan.textContent = count + 1;
    setting_tasks();
}

function removeTask(button, taskName) {
    const taskItem = button.parentNode.parentNode;
    taskItem.parentNode.removeChild(taskItem);

    const option = document.getElementById(taskName);
    option.style.display = 'block';
    setting_tasks();
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
            accountNum.className = 'account-num';
            accountNum.id = account;
            accountNum.innerHTML = `
                <span>${account}</span>
                <div>
                    <button onclick="changeAccount(${account})">选择</button>
                    <button onclick="deleteAccount(${account})">删除</button>
                </div>
                `;
            changePage.insertBefore(accountNum, contentItem);
        });
        Object.keys(config.users[account].task).forEach(challenge => {
            Object.keys(config.users[account].task[challenge]).forEach(taskName => {
                const taskCount = config.users[account].task[challenge][taskName];
                const option = document.getElementById(taskName);
                option.style.display = 'none';
                const taskItem = document.createElement('div');
                taskItem.className = 'task-item';
                taskItem.innerHTML = `
                                <span class="name">${taskName}</span>
                                <div>
                                    <button onclick="decrement(this)">-</button>
                                    <span class="task-count">${taskCount}</span>
                                    <button onclick="increment(this)">+</button>
                                    <button onclick="removeTask(this, '${taskName}')">删除</button>
                                </div>
                            `;
                const challengePage = document.getElementById(challenge)
                const addTaskDiv = challengePage.querySelector('.add_task');
                challengePage.insertBefore(taskItem, addTaskDiv);
            });
        }
        )
        const dailyTraining = config.users[account].dailyTraining;
        const dailyTrainingSwitch = document.getElementById('dailyTrainingSwitch');
        dailyTrainingSwitch.checked = dailyTraining;
        const assignments = config.users[account].assignments;
        const assignmentsSwitch = document.getElementById('assignmentsSwitch');
        assignmentsSwitch.checked = assignments;
        const autoClose = config.auto_close;
        const autoCloseSwitch = document.getElementById('autoCloseSwitch');
        autoCloseSwitch.checked = autoClose;
    }
}

window.onload = function () {
    setTimeout(load_config, 500);
}

async function setting_tasks() {
    const tasks = {};
    const account = document.querySelector('.account').textContent;
    const challenges = ["Planar_Ornaments", "Calyx_Golden", "Calyx_Crimson", "Stagnant_Shadows", "Cavern_Relic_Sets", "Echo_of_War"];
    challenges.forEach(challengeName => {
        tasks[challengeName] = {};
        const taskItems = document.getElementById(challengeName).querySelectorAll('.task-item');
        taskItems.forEach(taskItem => {
            const taskName = taskItem.querySelector('.name').textContent;
            const taskCount = parseInt(taskItem.querySelector('.task-count').textContent);
            tasks[challengeName][taskName] = taskCount;
        });
    });
    await pywebview.api.setting_tasks(account, tasks);
}

async function start() {
    await pywebview.api.start();

}

document.addEventListener('DOMContentLoaded', (event) => {
    const dailyTrainingSwitch = document.getElementById('dailyTrainingSwitch');
    const assignmentsSwitch = document.getElementById('assignmentsSwitch');
    const autoCloseSwitch = document.getElementById('autoCloseSwitch');

    if (dailyTrainingSwitch) {
        dailyTrainingSwitch.addEventListener('change', async (event) => {
            const account = document.querySelector('.account').textContent;
            const dailyTraining = event.target.checked;
            // 在这里添加你需要执行的逻辑，例如保存设置到配置文件
            await pywebview.api.set_daily_training(account, dailyTraining);
        });
    }

    if (assignmentsSwitch) {
        assignmentsSwitch.addEventListener('change', async (event) => {
            const account = document.querySelector('.account').textContent;
            const assignments = event.target.checked;
            // 在这里添加你需要执行的逻辑，例如保存设置到配置文件
            await pywebview.api.set_assignments(account, assignments);
        });
    }

    if (autoCloseSwitch) {
        autoCloseSwitch.addEventListener('change', async (event) => {
            const autoClose = event.target.checked;
            // 在这里添加你需要执行的逻辑，例如保存设置到配置文件
            await pywebview.api.set_autoClose(autoClose);
        });
    }
});