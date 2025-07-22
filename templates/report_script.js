const length_check_rows = ['Title', 'Description', 'OG Title', 'OG Description'];

function showTab(tabIndex) {
    document.querySelectorAll('.tab-button').forEach((tab, index) => tab.classList.toggle('active', index === tabIndex));
    document.querySelectorAll('.tab-content').forEach((content, index) => content.classList.toggle('active', index === tabIndex));
}

function updateLength(field) {
    const length = field.textContent.length;
    const counterCell = field.closest('tr').querySelector('.len-counter-fix');
    if (counterCell) counterCell.textContent = `${length}자`;
}

function handleHighlight(cell, isIssue) {
    if (!cell) return;
    cell.dataset.status = isIssue ? 'issue' : 'ok';
    if (isIssue) cell.classList.add('highlight-cell');
    else cell.classList.remove('highlight-cell');
}

function initSeoQaHandlers() {
    document.querySelectorAll('.seo-table .editable-field').forEach(field => {
        const cell = field.closest('td');
        if (!cell) return;
        const factorName = field.closest('tr').querySelector('.factor-name').textContent.trim();
        const initialHandler = () => handleHighlight(cell, cell.dataset.status === 'issue');

        if (cell.classList.contains('comment-cell')) {
            field.addEventListener('input', () => {
                const text = field.textContent.trim().toLowerCase();
                handleHighlight(cell, !(text === '이슈 없음' || text === 'n/a' || text === ''));
            });
        } else if (cell.classList.contains('fix-cell') && length_check_rows.includes(factorName)) {
            field.addEventListener('input', () => updateLength(field));
            updateLength(field);
        }
        initialHandler();
    });
}

function initAltTableHandlers() {
    // Alt text 토글 버튼 기능 수정
    document.querySelectorAll('.alt-table .alt-comment-toggle').forEach(toggle => {
        const cell = toggle.closest('td');
        const toggleHandler = () => {
            const isIssue = toggle.textContent.trim() === '수정 필요';
            handleHighlight(cell, isIssue);
        };
        
        toggle.addEventListener('click', () => {
            toggle.textContent = (toggle.textContent === '이슈 없음') ? '수정 필요' : '이슈 없음';
            toggleHandler();
        });
        
        toggleHandler(); // 페이지 로드 시 초기 하이라이트 적용
    });

    // Alt text 정렬 기능 수정
    document.querySelectorAll('.alt-table th.sortable').forEach(header => {
        header.addEventListener('click', () => {
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            if (!tbody) return;
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const colIndex = header.cellIndex;
            const currentOrder = header.dataset.sortOrder || 'desc';
            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
            header.dataset.sortOrder = newOrder;

            rows.sort((a, b) => {
                const aText = a.children[colIndex].textContent.trim();
                const bText = b.children[colIndex].textContent.trim();
                let comparison = aText.localeCompare(bText, 'ko');
                return newOrder === 'asc' ? comparison : -comparison;
            });
            rows.forEach(row => tbody.appendChild(row));
            header.querySelector('.sort-icon').innerHTML = newOrder === 'asc' ? '&#9650;' : '&#9660;';
        });
    });
}

function initTabScrolling() {
    const tabContainer = document.querySelector('.tab-container');
    if (!tabContainer) return;
    const leftArrow = document.querySelector('.scroll-arrow.left');
    const rightArrow = document.querySelector('.scroll-arrow.right');
    leftArrow.addEventListener('click', () => { tabContainer.scrollLeft -= 200; });
    rightArrow.addEventListener('click', () => { tabContainer.scrollLeft += 200; });
}

function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    return text.replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m]));
}

function exportStaticReport() {
    const staticScript = `function showTab(t){document.querySelectorAll('.tab-button').forEach((e,n)=>e.classList.toggle('active',n===t));document.querySelectorAll('.tab-content').forEach((e,n)=>e.classList.toggle('active',n===t))}document.addEventListener('DOMContentLoaded',()=>showTab(0));`;
    let staticHtml = `<!DOCTYPE html><html lang='ko'><head><meta charset='UTF-8'><title>${escapeHtml(document.title)} (Final)</title>`;
    staticHtml += `<style>${document.querySelector('style').innerHTML}</style>`;
    staticHtml += `<scr` + `ipt>${staticScript}</scr` + `ipt></head><body>`;
    staticHtml += `<div class='main-container'><h2>${escapeHtml(document.querySelector('h2').innerText)} (Final)</h2>`;
    staticHtml += document.querySelector('.tabs-wrapper').outerHTML;
    
    document.querySelectorAll('.tab-content').forEach(content => {
        let newContent = content.cloneNode(true);
        newContent.querySelectorAll('.editable-field, .alt-comment-toggle').forEach(field => {
            const parent = field.parentElement;
            if (parent.dataset.status === 'issue') parent.classList.add('highlight-cell');
            else parent.classList.remove('highlight-cell');
            field.replaceWith(document.createTextNode(field.textContent));
        });
        newContent.querySelectorAll('.len-counter-fix').forEach(counter => {
            counter.parentElement.innerHTML = escapeHtml(counter.textContent);
        });
        staticHtml += newContent.outerHTML;
    });

    staticHtml += `</div></body></html>`;
    const blob = new Blob([staticHtml], { type: 'text/html;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = (document.querySelector('h2').innerText.replace(/ /g, '_') + '_Final.html');
    link.click();
    URL.revokeObjectURL(link.href);
}

function exportToExcel() {
    try {
        if (typeof XLSX === 'undefined') {
            throw new Error("SheetJS 라이브러리를 찾을 수 없습니다. templates 폴더에 sheetjs.min.js 파일이 있는지 확인해주세요.");
        }

        const wb = XLSX.utils.book_new();
        const ticketName = document.querySelector('h2').innerText.split(' - ')[1] || 'Report';

        document.querySelectorAll('.tab-content').forEach((tabContent, index) => {
            // Excel 시트 이름 로직 수정
            let sheetName = document.querySelector(`.tab-button[onclick='showTab(${index})']`).textContent.trim();
            if (sheetName.length > 31) {
                sheetName = sheetName.substring(sheetName.length - 31);
            }
            sheetName = sheetName.replace(/[\\/*?:\\[\\]]/g, '_');
            
            const sheetData = [];
            
            const seoTable = tabContent.querySelector('.seo-table');
            if (seoTable) {
                sheetData.push(["SEO QA"]); 
                const headers = Array.from(seoTable.querySelectorAll('thead th')).map(th => th.textContent.trim());
                sheetData.push(headers);
                seoTable.querySelectorAll('tbody tr').forEach(row => {
                    const rowData = Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim());
                    sheetData.push(rowData);
                });
            }

            sheetData.push([]); 

            const altTable = tabContent.querySelector('.alt-table');
            if (altTable) {
                sheetData.push(["Image Alt QA"]);
                const altHeaders = Array.from(altTable.querySelectorAll('thead th'))
                    .filter((th, idx) => idx !== 1) 
                    .map(th => th.textContent.replace(/[\u25B2\u25BC\u2195]/g, '').trim());
                sheetData.push(altHeaders);

                altTable.querySelectorAll('tbody tr').forEach(row => {
                    const rowData = Array.from(row.querySelectorAll('td'))
                        .filter((td, idx) => idx !== 1)
                        .map(td => td.textContent.trim());
                    sheetData.push(rowData);
                });
            }
            
            const ws = XLSX.utils.aoa_to_sheet(sheetData);
            XLSX.utils.book_append_sheet(wb, ws, sheetName);
        });
        
        const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
        XLSX.writeFile(wb, `${ticketName}_${today}.xlsx`);

    } catch (e) {
        console.error(e);
        alert("Excel 내보내기 중 오류가 발생했습니다: " + e.message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    showTab(0);
    initSeoQaHandlers();
    initAltTableHandlers();
    initTabScrolling();
});