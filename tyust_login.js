const CryptoJS = require('crypto-js');

const generate_csrf_key = (count = 32) => {
    const t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        , e = t.length;
    let o = "";
    for (let i = 0; i < count; i++)
        o += t.charAt(Math.floor(Math.random() * e));
    return o
}

function generateDesKey() {
    const n = CryptoJS.lib.WordArray.random(8);
    return CryptoJS.enc.Base64.stringify(n)
}

function get_crypto_and_password(password) {
    const crypto = generateDesKey();
    const enc = CryptoJS.enc.Base64.parse(crypto)
    let password_str = CryptoJS.DES.encrypt(password, enc, {
        mode: CryptoJS.mode.ECB,
        padding: CryptoJS.pad.Pkcs7
    }).toString()
    return {crypto, password_str}
}

function get_csrf_key_and_value() {
    const csrf_key = generate_csrf_key();
    const temp = btoa(csrf_key)
    const middle_crypto = temp.substring(0, temp.length / 2) + temp + temp.substring(temp.length / 2, temp.length);
    const csrf_value = CryptoJS.MD5(middle_crypto).toString()
    return {csrf_key, csrf_value}
}