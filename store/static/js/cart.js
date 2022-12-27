let updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        let productId = this.dataset.product
        let action = this.dataset.action
        let id = this.dataset.id
        // console.log('productId:', productId, 'Action:', action)
        // console.log('USER:', user)

        if (user === 'AnonymousUser') {
            // console.log('User is not authenticated')
            addCookieItem(productId, action)
        } else {
            updateUserOrder(productId, action, id)
        }
    })
}

function updateUserOrder(productId, action, id) {
    // console.log('User is authenticated, sending data...')
    let total_price;
    let price;
    let url = '/update/'
    let data = {'productId': productId, 'action': action}
    if (id !== undefined && id.startsWith('quantity')) {
        let itemId = id.slice(-1)
        data = {'productId': productId, 'action': action, 'item': true}
        price = document.getElementById('item-price' + itemId)
        total_price = document.getElementById('total-price' + itemId)
    }
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            if (id !== undefined && id.startsWith('quantity')) {
                let orderItem = document.getElementById(id)
                let new_price = (parseFloat(price.outerText.replace('$', '')) * data.orderItem).toFixed(2)
                total_price.innerHTML = '$' + new_price.toString()
                orderItem.innerHTML = data.orderItem
                let total_items = document.getElementsByName('cart-total')
                for (let i = 0; i < total_items.length; i++) {
                    total_items[i].innerHTML = data.get_cart_items
                }
                total_price = document.getElementById('total-price')
                total_price.innerHTML = ' $' + data.get_cart_total
            } else {
                let total_items = document.getElementById('cart-total')
                total_items.innerHTML = data.get_cart_items
            }
        });
}


function addCookieItem(productId, action) {
    console.log('User is not authenticated')

    if (action === 'add') {
        if (cart[productId] === undefined) {
            cart[productId] = {'quantity': 1}

        } else {
            cart[productId]['quantity'] += 1
        }
    }

    if (action === 'remove') {
        cart[productId]['quantity'] -= 1

        if (cart[productId]['quantity'] <= 0) {
            console.log('Item should be deleted')
            delete cart[productId];
        }
    }
    console.log('CART:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

    location.reload()
}