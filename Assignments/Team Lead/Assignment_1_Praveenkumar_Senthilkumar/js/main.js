let resume = document.getElementById('resume')
let download = document.getElementById('download');

function generatePdf() {
	html2pdf(resume);
}

download.addEventListener('click', () => {
	generatePdf()
})