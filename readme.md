# ToysRUs AutoBuy Monitor

A Python script that monitors ToysRUs Malaysia product pages and notifies you via email (using AppleScript Mail) when items are in stock and automatically adds them to your cart.

## Prerequisites

- Python 3.7+
- [pip](https://pip.pypa.io/en/stable/)
- macOS (for AppleScript Mail integration)

## Installation

1. **Clone the repository** (if not already):

   ```sh
   git clone https://github.com/Kaitbh/toyrusmy-bot-addcart
   ```

2. **Run the bootstrap script** to set up a virtual environment and install dependencies:

   ```sh
   bash bootstrap.sh
   ```

   This will:

   - Create and activate a Python virtual environment
   - Install required Python packages
   - Install Playwright browsers

## Getting Started

1. **Add product URLs**  
   Edit `product_urls.txt` and add one ToysRUs Malaysia product URL per line.

2. **Authentication**  
   On first run, you will be prompted to log in manually in the browser window. Your session will be saved for future runs.

## Usage

Run the script with your sender and receiver email addresses:

```sh
source venv/bin/activate
python main.py --sender "your@email.com" --receiver "destination@email.com"
```

- `--sender`: The email address configured in Apple Mail (must match an account in Mail).
- `--receiver`: The email address to receive notifications.
- `--refresh-time`: _(Optional)_ Interval in seconds between stock checks (default: 15).

Example with custom refresh time:

```sh
python main.py --sender "me@icloud.com" --receiver "friend@gmail.com" --refresh-time 30
```

## How It Works

- Monitors each product page for the "Add to Cart" button.
- When available, adds the item to your cart and sends an email notification.
- Continues until all listed items are added or the script is stopped.

## Notes

- The script uses AppleScript to send emails via the Mail app (macOS only).
- Your login session is saved in `auth_state.json` for convenience.
- Make sure your sender email is set up in the Mail app and allowed to send messages.

## Troubleshooting

- If you encounter login issues, delete `auth_state.json` and re-run the script to re-authenticate.
- Ensure Playwright browsers are installed (`python -m playwright install`).

## License

MIT License
