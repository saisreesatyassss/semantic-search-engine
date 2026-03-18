# Setup script for Streamlit Cloud
mkdir -p ~/.streamlit/

# Create credentials file (optional, prevents interactive prompt)
cat << EOF > ~/.streamlit/credentials.toml
[general]
email = ""
EOF

echo "Setup complete!"
