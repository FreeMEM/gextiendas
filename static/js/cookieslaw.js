function controlcookies() {
	// si variable no existe se crea (al clicar en Aceptar)
	
	localStorage.controlcookie++; // incrementamos cuenta de la cookie
	cookie1.style.display='none'; // Esconde la política de cookies
	

}
localStorage.controlcookie = (localStorage.controlcookie || 0);
if (localStorage.controlcookie==0){ 
	jQuery('#cookie1').removeClass('hide');
	/*document.getElementById('cookie1').style.bottom = '-50px';*/
} 