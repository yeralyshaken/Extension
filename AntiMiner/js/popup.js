(function () {

    'use strict';
    
    var utils;
    var url = "https://a1ad-2-135-65-250.eu.ngrok.io";

    function initPopupPage() {
        utils = chrome.extension.getBackgroundPage().utils;
        
        initWhiteListBtnStatus();

        document.getElementById('startButton').addEventListener('click', function (e) {
            chrome.runtime.sendMessage({action: 'mbStart'}, utils.noop);
            chrome.extension.getBackgroundPage().updateIcon(true);
            chrome.tabs.reload();
            window.close();
        });

        document.getElementById('pauseButton').addEventListener('click', function (e) {
            chrome.runtime.sendMessage({action: 'mbPause'}, utils.noop);
            chrome.extension.getBackgroundPage().updateIcon(false);
            chrome.tabs.reload();
            window.close();
        });

        document.getElementById('singin').addEventListener('click', function (e) {
            const loginUrl = url + '/login';
            window.open(loginUrl, '_blank').focus();
            // chrome.runtime.sendMessage({action: 'mbStart'}, utils.noop);
            chrome.tabs.reload();
            window.close();
        });

        document.getElementById('dashboard').addEventListener('click', function (e) {
            const homeUrl = url + '/home';
            window.open(homeUrl, '_blank').focus();
            // chrome.runtime.sendMessage({action: 'mbPause'}, utils.noop);
            chrome.tabs.reload();
            window.close();
        });

        // // document.getElementById('token').innerText = getToken();
        // document.getElementById('settingsBtn').addEventListener('click', function (e) {
        //     chrome.runtime.openOptionsPage();
        //     window.close();
        // });

        // document.getElementById('addWlist').addEventListener('click', function (e) {
        //     chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        //         if(!tabs) {
        //             return;
        //         }
        //         let ctab = tabs[0];
        //         if(utils.isSpecialTab(ctab)) {
        //             return;
        //         }
        //         chrome.runtime.sendMessage({action: 'addWlist', tab : ctab}, utils.noop);
        //         chrome.tabs.reload(ctab.tabId);
        //         window.close();
        //     });
        // });

        // document.getElementById('removeWlist').addEventListener('click', function (e) {
        //     chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        //         if(!tabs) {
        //             return;
        //         }
        //         let ctab = tabs[0];
        //         chrome.runtime.sendMessage({action: 'removeWlist', tab : ctab}, utils.noop);
        //         chrome.tabs.reload(ctab.tabId);
        //         window.close();
        //     });
        // });

    }

    function initWhiteListBtnStatus() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if(!tabs) {
                return;
            }
            let ctab = tabs[0];
            initSuspendBtn(ctab.id);
            // let domain = utils.getDomain(ctab.url);
            // let wlistStatus = utils.checkWhiteList(domain, chrome.extension.getBackgroundPage().mbSettings['mbWhiteList']);

            // if(wlistStatus) {
            //     setWlistStatus(true);
                
            // } else {
            //     setWlistStatus(false);
            //     initSuspendBtn(ctab.id);
            // }
        });
    }

    function initSuspendBtn(tabId) {
        utils.getOption('mbRunStatus', function(value) {
            setBtnStatus(value);
            chrome.extension.getBackgroundPage().updateIcon(value);
            initBlockCount(tabId);
        });
    }

    function initBlockCount(tabId) {
        let mbTabstmp = chrome.extension.getBackgroundPage().mbTabs;

        if(tabId in mbTabstmp) {
            document.getElementById('blockedNum').innerText = mbTabstmp[tabId].length;
            let prop,
                trEl,
                tdEl,
                tableEl = document.getElementById('blockedDomains');

            for(prop in mbTabstmp[tabId]) {
                trEl = document.createElement('tr');
                tdEl = document.createElement('td');
                tdEl.innerText = mbTabstmp[tabId][prop];
                trEl.appendChild(tdEl);
                tableEl.appendChild(trEl);
            }
        } else {
            document.getElementById('blockedNum').innerText = 0;
        }

    }

    function setWlistStatus(status) {
        document.getElementById('addWlist').style.display = (status === true) ? 'none' : '';
        document.getElementById('removeWlist').style.display = (status === true) ? '' : 'none';
        document.getElementById('hideWl').style.display = (status === true) ? 'none' : '';
    }

    function setBtnStatus(status) {
        document.getElementById('pauseButton').style.display = (status === true) ? '' : 'none';
        document.getElementById('startButton').style.display = (status === true) ? 'none' : '';
        document.getElementById('dashboard').style.display = (status === true) ? '' : 'none';
        document.getElementById('singin').style.display = (status === true) ? 'none' : '';
        document.getElementById('hidePs').style.display = (status === true) ? '' : 'none';
    }

    function loopEls(className, callback) {
        Array.prototype.forEach.call(document.getElementsByClassName(className), callback);
    }

    document.addEventListener('DOMContentLoaded', function () {
        initPopupPage();
    });

    async function getToken() {
        const authUrl = url + '/auth';

        var data = new FormData();
        data.append("username", "test");
        data.append("password", "test");

        var requestOptions = {
            method: 'POST',
            body: data,
            headers: {
                'Content-Type': 'application/json'
            },
            redirect: 'follow'
        };

        const response = await fetch(authUrl, requestOptions);
        
        return await response.json();
    }
}());