(function () {
    cookie = {
        "p_skey": "-EOkpyRMwRSTR1J51KxeD9bBwvOhsQ1lzIEVYx2libg_",
        "skey": "@O4ccRYMr6",
    }
    var tmpSkey = null, tmpToken = null;
    return function () {
        var skey = cookie['p_skey'] || cookie['skey'] || '', hash = 5381, token = tmpToken;

        if (skey) {
            //只有缓存中的skey失效时才重新生成gtoken
            if (skey !== tmpSkey) {
                tmpSkey = skey;
                var i = 0, l = skey.length;
                for (; i < l; ++i) {
                    hash += (hash << 5) + skey.charAt(i).charCodeAt();
                }
                tmpToken = token = hash & 0x7fffffff;
            }
        } else {
            //不存在skey时,不需要token
            tmpToken = token = null;
        }
        console.log(token);
        return token;
    };
})()()
