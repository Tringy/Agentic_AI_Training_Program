/**
 * ES6 Class example demonstrating object-oriented patterns in JavaScript.
 */

/**
 * Represents a shopping cart with items and total calculation.
 */
class ShoppingCart {
  constructor() {
    this.items = [];
    this.discount = 0;
  }

  /**
   * Add an item to the cart
   * @param {Object} item - Item object with name, price, and quantity
   */
  addItem(item) {
    if (!item.name || !item.price || !item.quantity) {
      throw new Error('Item must have name, price, and quantity');
    }
    if (item.price < 0 || item.quantity < 1) {
      throw new Error('Invalid price or quantity');
    }
    this.items.push({ ...item });
  }

  /**
   * Remove an item from the cart by name
   * @param {string} itemName - Name of the item to remove
   * @returns {boolean} True if item was removed, false if not found
   */
  removeItem(itemName) {
    const index = this.items.findIndex(item => item.name === itemName);
    if (index !== -1) {
      this.items.splice(index, 1);
      return true;
    }
    return false;
  }

  /**
   * Apply a discount percentage to the cart
   * @param {number} percentage - Discount percentage (0-100)
   */
  applyDiscount(percentage) {
    if (percentage < 0 || percentage > 100) {
      throw new Error('Discount must be between 0 and 100');
    }
    this.discount = percentage;
  }

  /**
   * Calculate subtotal before discount
   * @returns {number} Subtotal amount
   */
  getSubtotal() {
    return this.items.reduce((total, item) => {
      return total + (item.price * item.quantity);
    }, 0);
  }

  /**
   * Calculate total after discount
   * @returns {number} Total amount after discount
   */
  getTotal() {
    const subtotal = this.getSubtotal();
    const discountAmount = subtotal * (this.discount / 100);
    return subtotal - discountAmount;
  }

  /**
   * Get cart summary
   * @returns {Object} Summary with items, subtotal, discount, and total
   */
  getSummary() {
    return {
      itemCount: this.items.length,
      items: this.items,
      subtotal: this.getSubtotal(),
      discount: this.discount,
      total: this.getTotal()
    };
  }
}

/**
 * Premium shopping cart with additional features
 */
class PremiumShoppingCart extends ShoppingCart {
  constructor() {
    super();
    this.rewardPoints = 0;
  }

  /**
   * Calculate reward points (1 point per dollar spent)
   * @returns {number} Reward points earned
   */
  calculateRewardPoints() {
    this.rewardPoints = Math.floor(this.getTotal());
    return this.rewardPoints;
  }

  /**
   * Get extended summary with reward points
   * @returns {Object} Summary including reward points
   */
  getSummary() {
    const baseSummary = super.getSummary();
    return {
      ...baseSummary,
      rewardPoints: this.calculateRewardPoints()
    };
  }
}

module.exports = { ShoppingCart, PremiumShoppingCart };
