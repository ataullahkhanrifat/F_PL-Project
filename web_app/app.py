#!/usr/bin/env python3
"""
FPL Squad Optimizer Web App

A Streamlit application for optimizing Fantasy Premier League squads
using machine learning predictions and linear programming.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
import os
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from optimizer import FPLOptimizer
    from fetch_fpl_data import FPLDataFetcher
except ImportError:
    st.error("Could not import required modules. Please ensure you're running from the project root.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="FPL Squad Optimizer",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light theme
st.markdown("""
<script>
    // Function to apply button styling
    function styleButtons() {
        // Style all buttons
        const buttons = window.parent.document.querySelectorAll('button, [role="button"]');
        buttons.forEach(button => {
            button.style.backgroundColor = '#37003c';
            button.style.color = '#ffffff';
            button.style.border = '2px solid #37003c';
            button.style.borderRadius = '0.5rem';
            button.style.fontWeight = '600';
            
            // Style button text content
            const textElements = button.querySelectorAll('span, p, div, *');
            textElements.forEach(el => {
                el.style.color = '#ffffff';
                el.style.fontWeight = '600';
            });
            
            // Add hover effect
            button.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#5a0066';
                this.style.borderColor = '#5a0066';
            });
            
            button.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '#37003c';
                this.style.borderColor = '#37003c';
            });
        });
        
        // Specifically target sidebar buttons
        const sidebarButtons = window.parent.document.querySelectorAll('[data-testid="stSidebar"] button, .css-1d391kg button, .css-1cypcdb button');
        sidebarButtons.forEach(button => {
            button.style.backgroundColor = '#37003c';
            button.style.color = '#ffffff';
            button.style.border = '2px solid #37003c';
            button.style.borderRadius = '0.5rem';
            button.style.fontWeight = '600';
            button.style.width = '100%';
            button.style.marginBottom = '0.5rem';
            
            // Force all child elements to white text
            const allChildren = button.querySelectorAll('*');
            allChildren.forEach(child => {
                child.style.color = '#ffffff';
                child.style.backgroundColor = 'transparent';
            });
        });
    }
    
    // Force light theme
    const stApp = window.parent.document.querySelector('.stApp');
    if (stApp) {
        stApp.style.backgroundColor = '#ffffff';
        stApp.style.color = '#262730';
    }
    
    // Force sidebar light theme
    const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        sidebar.style.backgroundColor = '#f0f2f6';
        sidebar.style.color = '#262730';
    }
    
    // Force header light theme
    const header = window.parent.document.querySelector('[data-testid="stHeader"]');
    if (header) {
        header.style.backgroundColor = '#ffffff';
        header.style.color = '#262730';
    }
    
    // Apply button styling
    styleButtons();
    
    // Re-apply button styling when content changes
    const observer = new MutationObserver(function(mutations) {
        styleButtons();
    });
    
    observer.observe(window.parent.document.body, {
        childList: true,
        subtree: true
    });
    
    // Remove any dark theme classes
    const darkElements = window.parent.document.querySelectorAll('[class*="dark"], [class*="Dark"]');
    darkElements.forEach(el => {
        el.style.backgroundColor = '#ffffff';
        el.style.color = '#262730';
    });
    
    // Force theme attribute
    window.parent.document.documentElement.setAttribute('data-theme', 'light');
    window.parent.document.body.setAttribute('data-theme', 'light');
    
    // Function to fix dropdown options
    function fixDropdownOptions() {
        // Target all dropdown option elements
        const dropdownOptions = window.parent.document.querySelectorAll(
            '[data-baseweb="popover"] li, ' +
            '[data-baseweb="menu"] li, ' +
            '[data-baseweb="select"] li, ' +
            '.stSelectbox li, ' +
            '[role="option"], ' +
            '[data-testid="stSelectbox"] li, ' +
            '[data-baseweb="popover"] div, ' +
            '[data-baseweb="menu"] div, ' +
            '[data-baseweb="select"] div'
        );
        
        dropdownOptions.forEach(option => {
            // Default state
            if (!option.hasAttribute('aria-selected') || option.getAttribute('aria-selected') === 'false') {
                option.style.backgroundColor = '#ffffff';
                option.style.color = '#262730';
                // Force all child elements to inherit color
                const children = option.querySelectorAll('*');
                children.forEach(child => {
                    child.style.color = '#262730';
                });
            }
            
            // Hover state
            option.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#37003c';
                this.style.color = '#ffffff';
                // Force all child elements to white
                const children = this.querySelectorAll('*');
                children.forEach(child => {
                    child.style.color = '#ffffff';
                });
            });
            
            option.addEventListener('mouseleave', function() {
                if (!this.hasAttribute('aria-selected') || this.getAttribute('aria-selected') === 'false') {
                    this.style.backgroundColor = '#ffffff';
                    this.style.color = '#262730';
                    // Force all child elements back to dark
                    const children = this.querySelectorAll('*');
                    children.forEach(child => {
                        child.style.color = '#262730';
                    });
                }
            });
            
            // Selected state
            if (option.hasAttribute('aria-selected') && option.getAttribute('aria-selected') === 'true') {
                option.style.backgroundColor = '#37003c';
                option.style.color = '#ffffff';
                // Force all child elements to white
                const children = option.querySelectorAll('*');
                children.forEach(child => {
                    child.style.color = '#ffffff';
                });
            }
        });
        
        // Also fix the selected value display in the dropdown input
        const selectedValues = window.parent.document.querySelectorAll(
            '[data-baseweb="select"] [data-baseweb="select-dropdown"], ' +
            '[data-testid="stSelectbox"] [data-baseweb="select"] > div, ' +
            '.stSelectbox [data-baseweb="select"] > div'
        );
        
        selectedValues.forEach(selected => {
            if (selected.style.backgroundColor === 'rgb(55, 0, 60)' || selected.style.backgroundColor === '#37003c') {
                selected.style.color = '#ffffff';
                const children = selected.querySelectorAll('*');
                children.forEach(child => {
                    child.style.color = '#ffffff';
                });
            }
        });
        
        // Fix multiselect selected option buttons
        const multiselectButtons = window.parent.document.querySelectorAll(
            '[data-baseweb="tag"], ' +
            '[data-testid="stMultiSelect"] button, ' +
            '.stMultiSelect button, ' +
            '[data-baseweb="tag"] button, ' +
            '[data-baseweb="tag"] span, ' +
            '[data-baseweb="tag"] div'
        );
        
        multiselectButtons.forEach(button => {
            // Check if it has a dark background
            const computedStyle = window.getComputedStyle(button);
            const bgColor = computedStyle.backgroundColor;
            
            if (bgColor === 'rgb(55, 0, 60)' || bgColor === '#37003c' || 
                button.style.backgroundColor === 'rgb(55, 0, 60)' || 
                button.style.backgroundColor === '#37003c') {
                button.style.color = '#ffffff';
                button.style.backgroundColor = '#37003c';
                
                // Force all child elements to white
                const children = button.querySelectorAll('*');
                children.forEach(child => {
                    child.style.color = '#ffffff';
                    if (child.tagName === 'SVG') {
                        child.style.fill = '#ffffff';
                        child.style.color = '#ffffff';
                    }
                    if (child.tagName === 'PATH') {
                        child.style.fill = '#ffffff';
                        child.style.stroke = '#ffffff';
                    }
                });
                
                // Force SVG icons (like close/cross buttons) to be white
                const svgs = button.querySelectorAll('svg');
                svgs.forEach(svg => {
                    svg.style.fill = '#ffffff';
                    svg.style.color = '#ffffff';
                    const paths = svg.querySelectorAll('path');
                    paths.forEach(path => {
                        path.style.fill = '#ffffff';
                        path.style.stroke = '#ffffff';
                    });
                });
            }
        });
        
        // Fix all multiselect close/cross buttons specifically
        const closeButtons = window.parent.document.querySelectorAll(
            '[data-baseweb="tag"] [role="button"], ' +
            '[data-baseweb="tag"] button[title*="Remove"], ' +
            '[data-baseweb="tag"] button[aria-label*="Remove"], ' +
            '[data-testid="stMultiSelect"] [role="button"], ' +
            '.stMultiSelect [role="button"]'
        );
        
        closeButtons.forEach(closeBtn => {
            closeBtn.style.backgroundColor = 'transparent';
            closeBtn.style.color = '#ffffff';
            closeBtn.style.border = 'none';
            
            // Force all SVG elements to be white
            const svgs = closeBtn.querySelectorAll('svg');
            svgs.forEach(svg => {
                svg.style.fill = '#ffffff';
                svg.style.color = '#ffffff';
                svg.style.stroke = '#ffffff';
                const paths = svg.querySelectorAll('path');
                paths.forEach(path => {
                    path.style.fill = '#ffffff';
                    path.style.stroke = '#ffffff';
                });
            });
            
            // Force all text content to be white
            const allChildren = closeBtn.querySelectorAll('*');
            allChildren.forEach(child => {
                child.style.color = '#ffffff';
                if (child.tagName === 'SVG') {
                    child.style.fill = '#ffffff';
                    child.style.color = '#ffffff';
                }
                if (child.tagName === 'PATH') {
                    child.style.fill = '#ffffff';
                    child.style.stroke = '#ffffff';
                }
            });
        });
        
        // Fix number input controls
        const numberInputs = window.parent.document.querySelectorAll(
            '[data-testid="stNumberInput"] input, ' +
            '.stNumberInput input, ' +
            'input[type="number"]'
        );
        
        numberInputs.forEach(input => {
            input.style.backgroundColor = '#ffffff';
            input.style.color = '#262730';
            input.style.border = '1px solid #e0e0e0';
        });
        
        // Fix number input buttons (up/down arrows)
        const numberButtons = window.parent.document.querySelectorAll(
            '[data-testid="stNumberInput"] button, ' +
            '.stNumberInput button, ' +
            'input[type="number"] + button, ' +
            'button[aria-label="increment"], ' +
            'button[aria-label="decrement"]'
        );
        
        numberButtons.forEach(button => {
            button.style.backgroundColor = '#37003c';
            button.style.color = '#ffffff';
            button.style.border = '1px solid #37003c';
            button.style.borderRadius = '0.25rem';
            
            // Force all child elements to white
            const children = button.querySelectorAll('*');
            children.forEach(child => {
                child.style.color = '#ffffff';
                if (child.tagName === 'SVG') {
                    child.style.fill = '#ffffff';
                }
                if (child.tagName === 'PATH') {
                    child.style.fill = '#ffffff';
                    child.style.stroke = '#ffffff';
                }
            });
            
            // Force SVG icons to be white
            const svgs = button.querySelectorAll('svg');
            svgs.forEach(svg => {
                svg.style.fill = '#ffffff';
                svg.style.color = '#ffffff';
                const paths = svg.querySelectorAll('path');
                paths.forEach(path => {
                    path.style.fill = '#ffffff';
                    path.style.stroke = '#ffffff';
                });
            });
            
            // Force any text content to be white
            if (button.textContent) {
                button.style.color = '#ffffff';
            }
        });
    }
    
    // Apply dropdown fixes
    fixDropdownOptions();
    
    // Re-apply dropdown fixes when content changes
    const dropdownObserver = new MutationObserver(function(mutations) {
        fixDropdownOptions();
    });
    
    dropdownObserver.observe(window.parent.document.body, {
        childList: true,
        subtree: true
    });
</script>
""", unsafe_allow_html=True)

# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'optimizer'

# Custom CSS for Complete Light Theme
st.markdown("""
<style>
    /* Force light theme for entire app */
    .stApp {
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #ffffff !important;
        color: #262730 !important;
        padding-top: 2rem;
    }
    
    /* Sidebar styling - multiple selectors to ensure coverage */
    .css-1d391kg, 
    .css-1cypcdb,
    .css-1y4p8pa,
    .css-1lcbmhc,
    .css-17eq0hr,
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6 !important;
        color: #262730 !important;
    }
    
    /* Sidebar content */
    .css-1d391kg .element-container,
    .css-1cypcdb .element-container,
    section[data-testid="stSidebar"] .element-container {
        color: #262730 !important;
    }
    
    /* Sidebar headers */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #37003c !important;
    }
    
    /* Navigation bar / header */
    .css-18e3th9,
    .css-1avcm0n,
    .css-k1vhr4,
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    
    /* Top toolbar */
    .css-1544g2n,
    .css-18ni7ap,
    .css-6qob1r {
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    
    /* Headers and text */
    .main-header {
        font-size: 3rem;
        color: #37003c !important;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        background-color: transparent !important;
    }
    
    /* All text elements */
    p, span, div, label, .stMarkdown {
        color: #262730 !important;
    }
    
    /* Buttons and inputs - comprehensive styling */
    .stButton > button,
    button[kind="primary"],
    button[kind="secondary"],
    .stDownloadButton > button {
        background-color: #37003c !important;
        color: #ffffff !important;
        border: 2px solid #37003c !important;
        border-radius: 0.5rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover,
    button[kind="primary"]:hover,
    button[kind="secondary"]:hover,
    .stDownloadButton > button:hover {
        background-color: #5a0066 !important;
        color: #ffffff !important;
        border-color: #5a0066 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(55, 0, 60, 0.3) !important;
    }
    
    /* Primary button specific styling */
    button[kind="primary"] {
        background-color: #37003c !important;
        color: #ffffff !important;
        border: 2px solid #37003c !important;
    }
    
    /* Secondary button styling */
    button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #37003c !important;
        border: 2px solid #37003c !important;
    }
    
    button[kind="secondary"]:hover {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    /* Ensure button text is always visible */
    .stButton button span,
    .stDownloadButton button span {
        color: inherit !important;
        font-weight: 600 !important;
    }
    
    /* Selectboxes */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #262730 !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    .stSelectbox label {
        color: #262730 !important;
    }
    
    /* Dropdown options styling */
    .stSelectbox ul {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 0.5rem !important;
    }
    
    .stSelectbox li {
        background-color: #ffffff !important;
        color: #262730 !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stSelectbox li:hover {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    .stSelectbox li[aria-selected="true"] {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    /* Dropdown menu items - more specific selectors */
    [data-baseweb="select"] ul {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    [data-baseweb="select"] li {
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    
    [data-baseweb="select"] li:hover {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    [data-baseweb="select"] li[aria-selected="true"] {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    /* Dropdown options - BaseWeb selectors */
    [data-baseweb="menu"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 0.5rem !important;
    }
    
    [data-baseweb="menu"] li {
        background-color: #ffffff !important;
        color: #262730 !important;
        padding: 0.5rem 1rem !important;
    }
    
    [data-baseweb="menu"] li:hover {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    [data-baseweb="menu"] li[aria-selected="true"] {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #262730 !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    .stTextInput label {
        color: #262730 !important;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background-color: #ffffff !important;
        color: #262730 !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    .stMultiSelect label {
        color: #262730 !important;
    }
    
    /* Sliders */
    .stSlider > div > div {
        background-color: #ffffff !important;
    }
    
    .stSlider label {
        color: #262730 !important;
    }
    
    /* Number inputs */
    .stNumberInput > div > div > input {
        background-color: #ffffff !important;
        color: #262730 !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    .stNumberInput label {
        color: #262730 !important;
    }
    
    /* Number input container */
    .stNumberInput > div > div {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 0.5rem !important;
    }
    
    /* Number input buttons (up/down arrows) */
    .stNumberInput button,
    [data-testid="stNumberInput"] button,
    input[type="number"] + button,
    button[aria-label="increment"],
    button[aria-label="decrement"] {
        background-color: #37003c !important;
        color: #ffffff !important;
        border: 1px solid #37003c !important;
        border-radius: 0.25rem !important;
        padding: 0.25rem !important;
        margin: 0.125rem !important;
    }
    
    .stNumberInput button:hover,
    [data-testid="stNumberInput"] button:hover,
    input[type="number"] + button:hover,
    button[aria-label="increment"]:hover,
    button[aria-label="decrement"]:hover {
        background-color: #5a0066 !important;
        color: #ffffff !important;
        border-color: #5a0066 !important;
    }
    
    /* Number input button text */
    .stNumberInput button span,
    .stNumberInput button div,
    [data-testid="stNumberInput"] button span,
    [data-testid="stNumberInput"] button div {
        color: #ffffff !important;
    }
    
    /* Number input button arrows - specific targeting */
    .stNumberInput button::before,
    .stNumberInput button::after,
    [data-testid="stNumberInput"] button::before,
    [data-testid="stNumberInput"] button::after {
        color: #ffffff !important;
    }
    
    /* Force arrow symbols to be white */
    .stNumberInput button[aria-label*="increment"]::before,
    .stNumberInput button[aria-label*="decrement"]::before,
    [data-testid="stNumberInput"] button[aria-label*="increment"]::before,
    [data-testid="stNumberInput"] button[aria-label*="decrement"]::before {
        content: "";
        color: #ffffff !important;
    }
    
    /* Target the actual arrow text content */
    .stNumberInput button[title*="increment"],
    .stNumberInput button[title*="decrement"],
    .stNumberInput button[aria-label*="increment"],
    .stNumberInput button[aria-label*="decrement"],
    [data-testid="stNumberInput"] button[title*="increment"],
    [data-testid="stNumberInput"] button[title*="decrement"],
    [data-testid="stNumberInput"] button[aria-label*="increment"],
    [data-testid="stNumberInput"] button[aria-label*="decrement"] {
        color: #ffffff !important;
        background-color: #37003c !important;
        border: 1px solid #37003c !important;
    }
    
    /* All elements inside number input buttons */
    .stNumberInput button *,
    [data-testid="stNumberInput"] button * {
        color: #ffffff !important;
    }
    
    /* SVG icons in number input buttons */
    .stNumberInput button svg,
    [data-testid="stNumberInput"] button svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }
    
    .stNumberInput button svg path,
    [data-testid="stNumberInput"] button svg path {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }
    
    /* Number input spinners */
    .stNumberInput input[type="number"]::-webkit-outer-spin-button,
    .stNumberInput input[type="number"]::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
    
    .stNumberInput input[type="number"] {
        -moz-appearance: textfield;
    }
    
    /* Checkboxes */
    .stCheckbox label {
        color: #262730 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #f0f2f6 !important;
        color: #262730 !important;
    }
    
    .streamlit-expanderContent {
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    
    /* Force override any remaining dark elements */
    * {
        scrollbar-color: #cccccc #f0f2f6 !important;
    }
    
    /* Additional button fixes - target any missed elements */
    div[data-testid="stButton"] button,
    div[data-testid="stDownloadButton"] button {
        background-color: #37003c !important;
        color: #ffffff !important;
        border: 2px solid #37003c !important;
    }
    
    div[data-testid="stButton"] button:hover,
    div[data-testid="stDownloadButton"] button:hover {
        background-color: #5a0066 !important;
        color: #ffffff !important;
        border-color: #5a0066 !important;
    }
    
    /* Button text elements specifically */
    button p, button span, button div {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Any remaining button elements */
    [role="button"] {
        background-color: #37003c !important;
        color: #ffffff !important;
        border: 2px solid #37003c !important;
    }
    
    [role="button"]:hover {
        background-color: #5a0066 !important;
        color: #ffffff !important;
    }
    
    /* Force override for button containers */
    [data-testid="stButton"],
    [data-testid="stDownloadButton"] {
        background-color: transparent !important;
    }
    
    /* Streamlit button widget containers */
    .element-container button,
    .stButton button,
    .row-widget button {
        background-color: #37003c !important;
        color: #ffffff !important;
        border: 2px solid #37003c !important;
    }
    
    /* Ultimate fallback for any dark buttons */
    button:not([style*="background-color: #37003c"]) {
        background-color: #37003c !important;
        color: #ffffff !important;
        border: 2px solid #37003c !important;
    }
    
    /* Sidebar elements specifically */
    section[data-testid="stSidebar"] * {
        color: #262730 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #262730 !important;
    }
    
    section[data-testid="stSidebar"] label {
        color: #262730 !important;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #37003c;
        color: #262730;
    }
    
    /* Player cards */
    .player-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 0.5rem;
        border: 1px solid #e0e0e0;
        color: #262730;
    }
    
    /* Stats cards */
    .stats-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
        color: #262730;
    }
    
    /* Stats headers */
    .stats-header {
        color: #37003c;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
        background-color: transparent;
    }
    
    /* Navigation buttons */
    .nav-button {
        background-color: #37003c !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 0.5rem !important;
        margin: 0.25rem !important;
        cursor: pointer !important;
        font-weight: 600 !important;
    }
    .nav-button:hover {
        background-color: #5a0066 !important;
        color: white !important;
    }
    .nav-button.active {
        background-color: #00ff87 !important;
        color: #37003c !important;
    }
    
    /* Sidebar navigation buttons specifically - multiple selectors */
    section[data-testid="stSidebar"] .stButton > button,
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] [data-testid="stButton"] button,
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button,
    .css-1d391kg .stButton > button,
    .css-1cypcdb .stButton > button {
        background-color: #37003c !important;
        color: #ffffff !important;
        border: 2px solid #37003c !important;
        width: 100% !important;
        margin-bottom: 0.5rem !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover,
    section[data-testid="stSidebar"] button:hover,
    section[data-testid="stSidebar"] [data-testid="stButton"] button:hover,
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover,
    .css-1d391kg .stButton > button:hover,
    .css-1cypcdb .stButton > button:hover {
        background-color: #5a0066 !important;
        color: #ffffff !important;
        border-color: #5a0066 !important;
        box-shadow: 0 2px 4px rgba(55, 0, 60, 0.3) !important;
    }
    
    /* Ensure sidebar button text is visible - all possible text elements */
    section[data-testid="stSidebar"] .stButton button span,
    section[data-testid="stSidebar"] .stButton button p,
    section[data-testid="stSidebar"] .stButton button div,
    section[data-testid="stSidebar"] button span,
    section[data-testid="stSidebar"] button p,
    section[data-testid="stSidebar"] button div,
    .css-1d391kg .stButton button *,
    .css-1cypcdb .stButton button * {
        color: #ffffff !important;
        font-weight: 600 !important;
        background-color: transparent !important;
    }
    
    /* Force all sidebar buttons to use light theme */
    .css-1d391kg button,
    .css-1cypcdb button,
    .css-1y4p8pa button,
    .css-1lcbmhc button {
        background-color: #37003c !important;
        color: #ffffff !important;
        border: 2px solid #37003c !important;
    }
    
    /* Force light theme for various Streamlit elements */
    .stSelectbox > div > div {
        background-color: #ffffff;
        color: #262730;
    }
    
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #262730;
    }
    
    .stSlider > div > div {
        background-color: #ffffff;
    }
    
    /* Additional dropdown styling for Streamlit components */
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 0.5rem !important;
    }
    
    [data-baseweb="popover"] ul {
        background-color: #ffffff !important;
        border: none !important;
    }
    
    [data-baseweb="popover"] li {
        background-color: #ffffff !important;
        color: #262730 !important;
        padding: 0.5rem 1rem !important;
    }
    
    [data-baseweb="popover"] li:hover {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    [data-baseweb="popover"] li[aria-selected="true"] {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    /* Streamlit select dropdown options */
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    
    [data-testid="stSelectbox"] [data-baseweb="popover"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    [data-testid="stSelectbox"] [data-baseweb="popover"] ul {
        background-color: #ffffff !important;
    }
    
    [data-testid="stSelectbox"] [data-baseweb="popover"] li {
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    
    [data-testid="stSelectbox"] [data-baseweb="popover"] li:hover {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    [data-testid="stSelectbox"] [data-baseweb="popover"] li[aria-selected="true"] {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    /* Force white text for any dark background dropdown items */
    [data-baseweb="popover"] li[style*="background-color: rgb(55, 0, 60)"],
    [data-baseweb="popover"] li[style*="background-color: #37003c"],
    [data-baseweb="menu"] li[style*="background-color: rgb(55, 0, 60)"],
    [data-baseweb="menu"] li[style*="background-color: #37003c"],
    [data-baseweb="select"] li[style*="background-color: rgb(55, 0, 60)"],
    [data-baseweb="select"] li[style*="background-color: #37003c"] {
        color: #ffffff !important;
    }
    
    /* Force all dropdown text elements to inherit color */
    [data-baseweb="popover"] li *,
    [data-baseweb="menu"] li *,
    [data-baseweb="select"] li *,
    .stSelectbox li *,
    [role="option"] * {
        color: inherit !important;
    }
    
    /* Selected dropdown value styling */
    [data-baseweb="select"] [data-baseweb="select-dropdown"] {
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    
    [data-baseweb="select"] [data-baseweb="select-dropdown"][style*="background-color: rgb(55, 0, 60)"],
    [data-baseweb="select"] [data-baseweb="select-dropdown"][style*="background-color: #37003c"] {
        color: #ffffff !important;
    }
    
    [data-baseweb="select"] [data-baseweb="select-dropdown"] * {
        color: inherit !important;
    }
    
    /* Streamlit selectbox selected value */
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    
    [data-testid="stSelectbox"] [data-baseweb="select"] > div[style*="background-color: rgb(55, 0, 60)"],
    [data-testid="stSelectbox"] [data-baseweb="select"] > div[style*="background-color: #37003c"] {
        color: #ffffff !important;
    }
    
    [data-testid="stSelectbox"] [data-baseweb="select"] > div * {
        color: inherit !important;
    }
    
    /* Force correct colors for any dropdown with dark background */
    [data-baseweb="select"][style*="background-color: rgb(55, 0, 60)"],
    [data-baseweb="select"][style*="background-color: #37003c"] {
        color: #ffffff !important;
    }
    
    [data-baseweb="select"][style*="background-color: rgb(55, 0, 60)"] *,
    [data-baseweb="select"][style*="background-color: #37003c"] * {
        color: #ffffff !important;
    }
    
    /* Ultimate fallback for dropdown options */
    div[data-baseweb="popover"] ul li,
    div[data-baseweb="menu"] ul li {
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    
    div[data-baseweb="popover"] ul li:hover,
    div[data-baseweb="menu"] ul li:hover {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    div[data-baseweb="popover"] ul li[aria-selected="true"],
    div[data-baseweb="menu"] ul li[aria-selected="true"] {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    /* Force all child elements in dropdown options to inherit color */
    div[data-baseweb="popover"] ul li *,
    div[data-baseweb="menu"] ul li *,
    [data-baseweb="popover"] li *,
    [data-baseweb="menu"] li * {
        color: inherit !important;
    }
    
    /* Multiselect selected option buttons */
    [data-baseweb="tag"] {
        background-color: #37003c !important;
        color: #ffffff !important;
        border: 1px solid #37003c !important;
    }
    
    [data-baseweb="tag"] * {
        color: #ffffff !important;
    }
    
    [data-baseweb="tag"] button {
        background-color: #37003c !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    [data-baseweb="tag"] button * {
        color: #ffffff !important;
    }
    
    [data-baseweb="tag"] span {
        color: #ffffff !important;
    }
    
    /* Fix cross/close button SVG in multiselect tags */
    [data-baseweb="tag"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }
    
    [data-baseweb="tag"] svg path {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }
    
    [data-baseweb="tag"] button svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }
    
    [data-baseweb="tag"] button svg path {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }
    
    /* Fix all multiselect close/cross buttons specifically */
    [data-baseweb="tag"] [role="button"],
    [data-baseweb="tag"] button[title*="Remove"],
    [data-baseweb="tag"] button[aria-label*="Remove"],
    [data-testid="stMultiSelect"] [role="button"],
    .stMultiSelect [role="button"] {
        background-color: transparent !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    [data-baseweb="tag"] [role="button"] *,
    [data-baseweb="tag"] button[title*="Remove"] *,
    [data-baseweb="tag"] button[aria-label*="Remove"] *,
    [data-testid="stMultiSelect"] [role="button"] *,
    .stMultiSelect [role="button"] * {
        color: #ffffff !important;
    }
    
    [data-baseweb="tag"] [role="button"] svg,
    [data-baseweb="tag"] button[title*="Remove"] svg,
    [data-baseweb="tag"] button[aria-label*="Remove"] svg,
    [data-testid="stMultiSelect"] [role="button"] svg,
    .stMultiSelect [role="button"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
        stroke: #ffffff !important;
    }
    
    [data-baseweb="tag"] [role="button"] svg path,
    [data-baseweb="tag"] button[title*="Remove"] svg path,
    [data-baseweb="tag"] button[aria-label*="Remove"] svg path,
    [data-testid="stMultiSelect"] [role="button"] svg path,
    .stMultiSelect [role="button"] svg path {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }
    
    /* Ultimate fallback for any button inside multiselect tags */
    [data-baseweb="tag"] button,
    [data-testid="stMultiSelect"] [data-baseweb="tag"] button,
    .stMultiSelect [data-baseweb="tag"] button {
        background-color: transparent !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    [data-baseweb="tag"] button *,
    [data-testid="stMultiSelect"] [data-baseweb="tag"] button *,
    .stMultiSelect [data-baseweb="tag"] button * {
        color: #ffffff !important;
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }
    
    /* Streamlit multiselect selected items */
    [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    [data-testid="stMultiSelect"] [data-baseweb="tag"] * {
        color: #ffffff !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #37003c !important;
        color: #ffffff !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] * {
        color: #ffffff !important;
    }
    
    /* Force any dark background elements to have white text */
    [style*="background-color: rgb(55, 0, 60)"] {
        color: #ffffff !important;
    }
    
    [style*="background-color: rgb(55, 0, 60)"] * {
        color: #ffffff !important;
    }
    
    [style*="background-color: #37003c"] {
        color: #ffffff !important;
    }
    
    [style*="background-color: #37003c"] * {
        color: #ffffff !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f0f2f6;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        color: #262730;
        border: 1px solid #e0e0e0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #37003c;
        color: #ffffff;
    }
    
    /* Dataframes */
    .stDataFrame {
        background-color: #ffffff;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Success/Info/Warning boxes */
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .stInfo {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    
    .stWarning {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    /* Plotly charts background */
    .js-plotly-plot {
        background-color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_player_data():
    """Load and cache player data"""
    # Get the project root directory (parent of web_app)
    project_root = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(project_root, "data", "processed", "fpl_players_latest.csv")
    
    if not os.path.exists(data_path):
        return None
    
    return pd.read_csv(data_path)

@st.cache_data
@st.cache_data
def load_fixture_data():
    """Load and cache fixture data"""
    # Get the project root directory (parent of web_app)
    project_root = os.path.dirname(os.path.dirname(__file__))
    fixture_path = os.path.join(project_root, "data", "raw", "fpl_fixtures_latest.json")
    bootstrap_path = os.path.join(project_root, "data", "raw", "fpl_data_latest.json")
    
    if not os.path.exists(fixture_path) or not os.path.exists(bootstrap_path):
        return None, None
    
    try:
        import json
        with open(fixture_path, 'r') as f:
            fixtures = json.load(f)
        
        with open(bootstrap_path, 'r') as f:
            bootstrap = json.load(f)
        
        return fixtures, bootstrap
    except:
        return None, None

@st.cache_resource
def load_optimizer(budget):
    """Load and cache the optimizer"""
    return FPLOptimizer(budget=budget)

def display_squad_table(selected_players):
    """Display the optimized squad in a formatted table"""
    
    # Position order for display
    position_order = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
    
    for position in position_order:
        position_players = selected_players[selected_players['position'] == position]
        
        if len(position_players) > 0:
            st.subheader(f"{position}s ({len(position_players)})")
            
            # Create columns for better layout
            cols = st.columns([3, 2, 1, 1, 1])
            cols[0].write("**Player**")
            cols[1].write("**Team**")
            cols[2].write("**Cost**")
            cols[3].write("**Form**")
            cols[4].write("**Pred. Pts**")
            
            for _, player in position_players.iterrows():
                cols = st.columns([3, 2, 1, 1, 1])
                cols[0].write(player['name'])
                cols[1].write(player['team'])
                cols[2].write(f"£{player['cost']:.1f}m")
                cols[3].write(f"{player['form']:.1f}")
                cols[4].write(f"{player['predicted_points']:.1f}")
            
            st.divider()

def create_position_pie_chart(selected_players):
    """Create a pie chart showing position distribution"""
    position_counts = selected_players['position'].value_counts()
    
    fig = px.pie(
        values=position_counts.values,
        names=position_counts.index,
        title="Squad Composition by Position",
        color_discrete_sequence=['#37003c', '#00ff87', '#e90052', '#04f5ff']
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False)
    
    return fig

def create_team_distribution_chart(selected_players):
    """Create a bar chart showing team distribution"""
    team_counts = selected_players['team'].value_counts()
    
    fig = px.bar(
        x=team_counts.index,
        y=team_counts.values,
        title="Players per Team",
        labels={'x': 'Team', 'y': 'Number of Players'},
        color=team_counts.values,
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        coloraxis_showscale=False
    )
    
    return fig

def create_cost_vs_points_scatter(selected_players):
    """Create a scatter plot of cost vs predicted points"""
    fig = px.scatter(
        selected_players,
        x='cost',
        y='predicted_points',
        color='position',
        size='form',
        hover_data=['name', 'team'],
        title="Cost vs Predicted Points",
        labels={'cost': 'Cost (£m)', 'predicted_points': 'Predicted Points'}
    )
    
    fig.update_layout(showlegend=True)
    
    return fig

def create_fdr_fixture_table(fixtures_data, bootstrap_data, upcoming_gameweeks=5):
    """Create a comprehensive FDR fixture table"""
    if not fixtures_data or not bootstrap_data:
        return None
    
    # Create team mapping
    teams = {team['id']: team for team in bootstrap_data['teams']}
    
    # Get current gameweek
    current_gw = 1
    current_time = pd.Timestamp.now()
    
    for fixture in fixtures_data:
        if fixture['finished'] is False and fixture['kickoff_time']:
            try:
                kickoff = pd.to_datetime(fixture['kickoff_time'])
                if kickoff > current_time:
                    current_gw = fixture['event']
                    break
            except:
                continue
    
    # Collect upcoming fixtures
    fixture_list = []
    
    for fixture in fixtures_data:
        if (fixture['event'] and 
            fixture['event'] >= current_gw and 
            fixture['event'] < current_gw + upcoming_gameweeks and
            fixture['team_h'] and fixture['team_a']):
            
            home_team = teams.get(fixture['team_h'], {})
            away_team = teams.get(fixture['team_a'], {})
            
            if home_team and away_team:
                # Calculate FDR
                def strength_to_fdr(strength):
                    if strength >= 1400: return 5
                    elif strength >= 1300: return 4
                    elif strength >= 1200: return 3
                    elif strength >= 1100: return 2
                    else: return 1
                
                # Home team perspective
                home_attack_fdr = strength_to_fdr(away_team.get('strength_defence_away', 1200))
                home_defence_fdr = strength_to_fdr(away_team.get('strength_attack_away', 1200))
                home_overall_fdr = strength_to_fdr(away_team.get('strength_overall_away', 1200))
                
                # Away team perspective  
                away_attack_fdr = strength_to_fdr(home_team.get('strength_defence_home', 1200))
                away_defence_fdr = strength_to_fdr(home_team.get('strength_attack_home', 1200))
                away_overall_fdr = strength_to_fdr(home_team.get('strength_overall_home', 1200))
                
                # Add home team fixture
                fixture_list.append({
                    'gameweek': fixture['event'],
                    'team': home_team.get('name', 'Unknown'),
                    'opponent': away_team.get('name', 'Unknown'),
                    'venue': 'Home',
                    'attack_fdr': home_attack_fdr,
                    'defence_fdr': home_defence_fdr,
                    'overall_fdr': home_overall_fdr,
                    'kickoff_time': fixture.get('kickoff_time', ''),
                    'difficulty_color': get_fdr_color(home_overall_fdr)
                })
                
                # Add away team fixture
                fixture_list.append({
                    'gameweek': fixture['event'],
                    'team': away_team.get('name', 'Unknown'),
                    'opponent': home_team.get('name', 'Unknown'),
                    'venue': 'Away',
                    'attack_fdr': away_attack_fdr,
                    'defence_fdr': away_defence_fdr,
                    'overall_fdr': away_overall_fdr,
                    'kickoff_time': fixture.get('kickoff_time', ''),
                    'difficulty_color': get_fdr_color(away_overall_fdr)
                })
    
    return pd.DataFrame(fixture_list) if fixture_list else None

def get_fdr_color(fdr):
    """Get color for FDR rating"""
    if fdr <= 2:
        return "🟢"  # Green for easy
    elif fdr == 3:
        return "🟡"  # Yellow for average
    elif fdr == 4:
        return "🟠"  # Orange for difficult
    else:
        return "🔴"  # Red for very difficult

def create_stats_page(players_df):
    """Create the Stats page with various player statistics"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 FPL Player Statistics</h1>', unsafe_allow_html=True)
    st.markdown("**Comprehensive statistics and leaderboards for all Premier League players**")
    
    # Navigation buttons in the main area
    col1, col2, col3, col4, col5 = st.columns(5)
    with col3:
        if st.button("🔙 Back to Optimizer", key="back_to_optimizer"):
            st.session_state.current_page = 'optimizer'
            st.rerun()
    
    st.divider()
    
    # Filter by position
    st.sidebar.header("🔍 Filters")
    position_filter = st.sidebar.selectbox(
        "Filter by Position",
        ["All Positions"] + sorted(players_df['position'].unique().tolist()),
        help="Filter statistics by player position"
    )
    
    # Apply position filter
    if position_filter != "All Positions":
        filtered_df = players_df[players_df['position'] == position_filter].copy()
    else:
        filtered_df = players_df.copy()
    
    # Remove managers if they exist
    filtered_df = filtered_df[filtered_df['position'] != 'Manager']
    
    # Create tabs for different stats
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🥅 Goals & Assists", "⭐ Top Performers", "⏰ Playing Time", "💰 Value Analysis", "🏆 Elite Stats", "🎯 FDR Analysis"])
    
    with tab1:
        st.markdown("### 🥅 Goals and Assists Leaders")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">🎯 Top 10 Goal Scorers</div>', unsafe_allow_html=True)
            
            top_scorers = filtered_df.nlargest(10, 'goals_scored')[
                ['name', 'position', 'team', 'goals_scored', 'cost', 'total_points']
            ].reset_index(drop=True)
            top_scorers.index = top_scorers.index + 1
            
            st.dataframe(
                top_scorers,
                column_config={
                    "name": "Player",
                    "position": "Position",
                    "team": "Team",
                    "goals_scored": st.column_config.NumberColumn("Goals", format="%d"),
                    "cost": st.column_config.NumberColumn("Cost", format="£%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">🎯 Top 10 Assist Providers</div>', unsafe_allow_html=True)
            
            top_assists = filtered_df.nlargest(10, 'assists')[
                ['name', 'position', 'team', 'assists', 'cost', 'total_points']
            ].reset_index(drop=True)
            top_assists.index = top_assists.index + 1
            
            st.dataframe(
                top_assists,
                column_config={
                    "name": "Player",
                    "position": "Position", 
                    "team": "Team",
                    "assists": st.column_config.NumberColumn("Assists", format="%d"),
                    "cost": st.column_config.NumberColumn("Cost", format="£%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Goals + Assists Combined
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.markdown('<div class="stats-header">🔥 Top 10 Goal Contributions (Goals + Assists)</div>', unsafe_allow_html=True)
        
        filtered_df['goal_contributions'] = filtered_df['goals_scored'] + filtered_df['assists']
        top_contributors = filtered_df.nlargest(10, 'goal_contributions')[
            ['name', 'position', 'team', 'goals_scored', 'assists', 'goal_contributions', 'cost', 'total_points']
        ].reset_index(drop=True)
        top_contributors.index = top_contributors.index + 1
        
        st.dataframe(
            top_contributors,
            column_config={
                "name": "Player",
                "position": "Position",
                "team": "Team", 
                "goals_scored": st.column_config.NumberColumn("Goals", format="%d"),
                "assists": st.column_config.NumberColumn("Assists", format="%d"),
                "goal_contributions": st.column_config.NumberColumn("Total", format="%d"),
                "cost": st.column_config.NumberColumn("Cost", format="£%.1f"),
                "total_points": st.column_config.NumberColumn("Points", format="%d")
            },
            use_container_width=True,
            hide_index=False
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### ⭐ Top Performers")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">🏆 Top 10 Points Scorers</div>', unsafe_allow_html=True)
            
            top_points = filtered_df.nlargest(10, 'total_points')[
                ['name', 'position', 'team', 'total_points', 'points_per_game', 'cost']
            ].reset_index(drop=True)
            top_points.index = top_points.index + 1
            
            st.dataframe(
                top_points,
                column_config={
                    "name": "Player",
                    "position": "Position",
                    "team": "Team",
                    "total_points": st.column_config.NumberColumn("Total Points", format="%d"),
                    "points_per_game": st.column_config.NumberColumn("PPG", format="%.1f"),
                    "cost": st.column_config.NumberColumn("Cost", format="£%.1f")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">📈 Top 10 Form Players</div>', unsafe_allow_html=True)
            
            top_form = filtered_df[filtered_df['form'] > 0].nlargest(10, 'form')[
                ['name', 'position', 'team', 'form', 'total_points', 'cost']
            ].reset_index(drop=True)
            top_form.index = top_form.index + 1
            
            st.dataframe(
                top_form,
                column_config={
                    "name": "Player", 
                    "position": "Position",
                    "team": "Team",
                    "form": st.column_config.NumberColumn("Form", format="%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d"),
                    "cost": st.column_config.NumberColumn("Cost", format="£%.1f")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### ⏰ Playing Time Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">⏱️ Top 10 Average Minutes Per Game</div>', unsafe_allow_html=True)
            
            # Filter players with at least some playing time
            playing_players = filtered_df[filtered_df['minutes'] > 0].copy()
            top_minutes = playing_players.nlargest(10, 'minutes_per_game')[
                ['name', 'position', 'team', 'minutes_per_game', 'minutes', 'total_points']
            ].reset_index(drop=True)
            top_minutes.index = top_minutes.index + 1
            
            st.dataframe(
                top_minutes,
                column_config={
                    "name": "Player",
                    "position": "Position", 
                    "team": "Team",
                    "minutes_per_game": st.column_config.NumberColumn("Avg Min/Game", format="%.1f"),
                    "minutes": st.column_config.NumberColumn("Total Minutes", format="%d"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">🕐 Top 10 Total Minutes Played</div>', unsafe_allow_html=True)
            
            top_total_minutes = playing_players.nlargest(10, 'minutes')[
                ['name', 'position', 'team', 'minutes', 'minutes_per_game', 'total_points']
            ].reset_index(drop=True)
            top_total_minutes.index = top_total_minutes.index + 1
            
            st.dataframe(
                top_total_minutes,
                column_config={
                    "name": "Player",
                    "position": "Position",
                    "team": "Team", 
                    "minutes": st.column_config.NumberColumn("Total Minutes", format="%d"),
                    "minutes_per_game": st.column_config.NumberColumn("Avg Min/Game", format="%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 💰 Value Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">💎 Top 10 Cost Efficiency (Points per £)</div>', unsafe_allow_html=True)
            
            value_players = filtered_df[filtered_df['cost'] > 0].copy()
            top_value = value_players.nlargest(10, 'cost_efficiency')[
                ['name', 'position', 'team', 'cost_efficiency', 'total_points', 'cost']
            ].reset_index(drop=True)
            top_value.index = top_value.index + 1
            
            st.dataframe(
                top_value,
                column_config={
                    "name": "Player",
                    "position": "Position",
                    "team": "Team",
                    "cost_efficiency": st.column_config.NumberColumn("Points per £", format="%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d"),
                    "cost": st.column_config.NumberColumn("Cost", format="£%.1f")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">📊 Top 10 Most Expensive Players</div>', unsafe_allow_html=True)
            
            expensive_players = filtered_df.nlargest(10, 'cost')[
                ['name', 'position', 'team', 'cost', 'total_points', 'cost_efficiency']
            ].reset_index(drop=True)
            expensive_players.index = expensive_players.index + 1
            
            st.dataframe(
                expensive_players,
                column_config={
                    "name": "Player",
                    "position": "Position",
                    "team": "Team",
                    "cost": st.column_config.NumberColumn("Cost", format="£%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d"),
                    "cost_efficiency": st.column_config.NumberColumn("Value", format="%.1f")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### 🏆 Elite Performance Stats")
        
        # Position-specific elite stats
        if position_filter == "All Positions" or position_filter == "Goalkeeper":
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">🥅 Top 10 Goalkeepers (Clean Sheets & Saves)</div>', unsafe_allow_html=True)
            
            gk_df = filtered_df[filtered_df['position'] == 'Goalkeeper']
            if len(gk_df) > 0:
                top_gks = gk_df.nlargest(10, 'clean_sheets')[
                    ['name', 'team', 'clean_sheets', 'saves', 'total_points', 'cost']
                ].reset_index(drop=True)
                top_gks.index = top_gks.index + 1
                
                st.dataframe(
                    top_gks,
                    column_config={
                        "name": "Goalkeeper",
                        "team": "Team",
                        "clean_sheets": st.column_config.NumberColumn("Clean Sheets", format="%d"),
                        "saves": st.column_config.NumberColumn("Saves", format="%d"),
                        "total_points": st.column_config.NumberColumn("Points", format="%d"),
                        "cost": st.column_config.NumberColumn("Cost", format="£%.1f")
                    },
                    use_container_width=True,
                    hide_index=False
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # ICT Index Leaders
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.markdown('<div class="stats-header">🎭 Top 10 ICT Index (Influence, Creativity, Threat)</div>', unsafe_allow_html=True)
        
        top_ict = filtered_df.nlargest(10, 'ict_index')[
            ['name', 'position', 'team', 'ict_index', 'influence', 'creativity', 'threat', 'total_points']
        ].reset_index(drop=True)
        top_ict.index = top_ict.index + 1
        
        st.dataframe(
            top_ict,
            column_config={
                "name": "Player",
                "position": "Position",
                "team": "Team",
                "ict_index": st.column_config.NumberColumn("ICT Index", format="%.1f"),
                "influence": st.column_config.NumberColumn("Influence", format="%.1f"),
                "creativity": st.column_config.NumberColumn("Creativity", format="%.1f"),
                "threat": st.column_config.NumberColumn("Threat", format="%.1f"),
                "total_points": st.column_config.NumberColumn("Points", format="%d")
            },
            use_container_width=True,
            hide_index=False
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Ownership Analysis
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.markdown('<div class="stats-header">👥 Top 10 Most Owned Players</div>', unsafe_allow_html=True)
        
        most_owned = filtered_df.nlargest(10, 'selected_by_percent')[
            ['name', 'position', 'team', 'selected_by_percent', 'total_points', 'cost']
        ].reset_index(drop=True)
        most_owned.index = most_owned.index + 1
        
        st.dataframe(
            most_owned,
            column_config={
                "name": "Player",
                "position": "Position",
                "team": "Team",
                "selected_by_percent": st.column_config.NumberColumn("Ownership %", format="%.1f%%"),
                "total_points": st.column_config.NumberColumn("Points", format="%d"),
                "cost": st.column_config.NumberColumn("Cost", format="£%.1f")
            },
            use_container_width=True,
            hide_index=False
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab6:
        st.markdown("### 🎯 Fixture Difficulty Rating (FDR) Analysis")
        
        # Check if FDR data is available
        fdr_columns = ['fdr_attack', 'fdr_defence', 'fdr_overall']
        has_fdr_data = all(col in filtered_df.columns for col in fdr_columns)
        
        if has_fdr_data:
            st.info("📊 FDR Scale: 1 (Very Easy) → 5 (Very Difficult). Lower FDR = Easier fixtures.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="stats-card">', unsafe_allow_html=True)
                st.markdown('<div class="stats-header">⚔️ Easiest Attack Fixtures (Best for Forwards/Midfielders)</div>', unsafe_allow_html=True)
                
                attack_fdr = filtered_df.groupby('team')[['fdr_attack', 'fdr_overall']].mean().round(2)
                best_attack = attack_fdr.nsmallest(10, 'fdr_attack').reset_index()
                best_attack.index = best_attack.index + 1
                
                st.dataframe(
                    best_attack,
                    column_config={
                        "team": "Team",
                        "fdr_attack": st.column_config.NumberColumn("Attack FDR", format="%.2f"),
                        "fdr_overall": st.column_config.NumberColumn("Overall FDR", format="%.2f")
                    },
                    use_container_width=True,
                    hide_index=False
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="stats-card">', unsafe_allow_html=True)
                st.markdown('<div class="stats-header">🛡️ Easiest Defence Fixtures (Best for Defenders/Goalkeepers)</div>', unsafe_allow_html=True)
                
                defence_fdr = filtered_df.groupby('team')[['fdr_defence', 'fdr_overall']].mean().round(2)
                best_defence = defence_fdr.nsmallest(10, 'fdr_defence').reset_index()
                best_defence.index = best_defence.index + 1
                
                st.dataframe(
                    best_defence,
                    column_config={
                        "team": "Team",
                        "fdr_defence": st.column_config.NumberColumn("Defence FDR", format="%.2f"),
                        "fdr_overall": st.column_config.NumberColumn("Overall FDR", format="%.2f")
                    },
                    use_container_width=True,
                    hide_index=False
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            # FDR-adjusted top performers
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">🌟 Best FDR Value Players (Form × Easy Fixtures)</div>', unsafe_allow_html=True)
            
            # Calculate FDR-adjusted form if available
            if 'fdr_adjusted_form' in filtered_df.columns:
                best_fdr_value = filtered_df.nlargest(15, 'fdr_adjusted_form')[
                    ['name', 'position', 'team', 'form', 'fdr_overall', 'fdr_adjusted_form', 'cost', 'total_points']
                ].reset_index(drop=True)
                best_fdr_value.index = best_fdr_value.index + 1
                
                st.dataframe(
                    best_fdr_value,
                    column_config={
                        "name": "Player",
                        "position": "Position",
                        "team": "Team",
                        "form": st.column_config.NumberColumn("Form", format="%.1f"),
                        "fdr_overall": st.column_config.NumberColumn("FDR", format="%.1f"),
                        "fdr_adjusted_form": st.column_config.NumberColumn("FDR-Adj Form", format="%.1f"),
                        "cost": st.column_config.NumberColumn("Cost", format="£%.1f"),
                        "total_points": st.column_config.NumberColumn("Points", format="%d")
                    },
                    use_container_width=True,
                    hide_index=False
                )
            else:
                # Fallback calculation
                filtered_df_copy = filtered_df.copy()
                filtered_df_copy['fdr_value'] = filtered_df_copy['form'] * (6 - filtered_df_copy['fdr_overall']) / 5
                best_fdr_value = filtered_df_copy.nlargest(15, 'fdr_value')[
                    ['name', 'position', 'team', 'form', 'fdr_overall', 'fdr_value', 'cost', 'total_points']
                ].reset_index(drop=True)
                best_fdr_value.index = best_fdr_value.index + 1
                
                st.dataframe(
                    best_fdr_value,
                    column_config={
                        "name": "Player",
                        "position": "Position",
                        "team": "Team",
                        "form": st.column_config.NumberColumn("Form", format="%.1f"),
                        "fdr_overall": st.column_config.NumberColumn("FDR", format="%.1f"),
                        "fdr_value": st.column_config.NumberColumn("FDR Value", format="%.1f"),
                        "cost": st.column_config.NumberColumn("Cost", format="£%.1f"),
                        "total_points": st.column_config.NumberColumn("Points", format="%d")
                    },
                    use_container_width=True,
                    hide_index=False
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Upcoming fixtures info if available
            if 'next_opponent' in filtered_df.columns:
                st.markdown('<div class="stats-card">', unsafe_allow_html=True)
                st.markdown('<div class="stats-header">📅 Next Fixture Highlights</div>', unsafe_allow_html=True)
                
                # Show teams with easiest next fixtures
                next_fixtures = filtered_df.groupby('team')[['next_opponent', 'next_fixture_fdr', 'next_fixture_home']].first()
                next_fixtures = next_fixtures.nsmallest(10, 'next_fixture_fdr').reset_index()
                next_fixtures['fixture'] = next_fixtures.apply(
                    lambda x: f"vs {x['next_opponent']} ({'H' if x['next_fixture_home'] else 'A'})", axis=1
                )
                next_fixtures.index = next_fixtures.index + 1
                
                st.dataframe(
                    next_fixtures[['team', 'fixture', 'next_fixture_fdr']],
                    column_config={
                        "team": "Team",
                        "fixture": "Next Fixture",
                        "next_fixture_fdr": st.column_config.NumberColumn("FDR", format="%.1f")
                    },
                    use_container_width=True,
                    hide_index=False
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Add FDR Fixture Table
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">📅 Upcoming Fixtures FDR Table</div>', unsafe_allow_html=True)
            
            # Load fixture data
            fixtures_data, bootstrap_data = load_fixture_data()
            
            if fixtures_data and bootstrap_data:
                fixture_df = create_fdr_fixture_table(fixtures_data, bootstrap_data, upcoming_gameweeks=5)
                
                if fixture_df is not None and not fixture_df.empty:
                    # Add filters for the fixture table
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        selected_teams = st.multiselect(
                            "Filter by Teams",
                            options=sorted(fixture_df['team'].unique()),
                            default=[],
                            key="fixture_team_filter"
                        )
                    
                    with col2:
                        selected_gameweeks = st.multiselect(
                            "Filter by Gameweeks",
                            options=sorted(fixture_df['gameweek'].unique()),
                            default=sorted(fixture_df['gameweek'].unique()),
                            key="fixture_gw_filter"
                        )
                    
                    with col3:
                        max_fdr = st.slider(
                            "Max FDR to show",
                            min_value=1,
                            max_value=5,
                            value=5,
                            key="fixture_max_fdr"
                        )
                    
                    # Filter fixture table
                    filtered_fixtures = fixture_df.copy()
                    
                    if selected_teams:
                        filtered_fixtures = filtered_fixtures[filtered_fixtures['team'].isin(selected_teams)]
                    
                    if selected_gameweeks:
                        filtered_fixtures = filtered_fixtures[filtered_fixtures['gameweek'].isin(selected_gameweeks)]
                    
                    filtered_fixtures = filtered_fixtures[filtered_fixtures['overall_fdr'] <= max_fdr]
                    
                    # Sort by gameweek and team
                    filtered_fixtures = filtered_fixtures.sort_values(['gameweek', 'team']).reset_index(drop=True)
                    
                    # Display fixture table
                    st.dataframe(
                        filtered_fixtures[['gameweek', 'team', 'opponent', 'venue', 'difficulty_color', 'attack_fdr', 'defence_fdr', 'overall_fdr']],
                        column_config={
                            "gameweek": st.column_config.NumberColumn("GW", format="%d"),
                            "team": "Team",
                            "opponent": "Opponent",
                            "venue": "Venue",
                            "difficulty_color": st.column_config.TextColumn("Difficulty", help="🟢 Easy, 🟡 Average, 🟠 Hard, 🔴 Very Hard"),
                            "attack_fdr": st.column_config.NumberColumn("Attack FDR", format="%.0f"),
                            "defence_fdr": st.column_config.NumberColumn("Defence FDR", format="%.0f"),
                            "overall_fdr": st.column_config.NumberColumn("Overall FDR", format="%.0f")
                        },
                        use_container_width=True,
                        hide_index=True,
                        height=400
                    )
                    
                    st.markdown("**Legend:** 🟢 Very Easy (1-2) | 🟡 Average (3) | 🟠 Difficult (4) | 🔴 Very Difficult (5)")
                    
                else:
                    st.info("No upcoming fixtures found in the data.")
            else:
                st.info("💡 Fixture data not available. Run `python src/fetch_fpl_data.py` to fetch latest fixtures.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.warning("⚠️ FDR data not available in current dataset.")
    
    # Summary stats at bottom
    st.divider()
    st.markdown("### 📈 Quick Statistics Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Players",
            len(filtered_df),
            f"Position: {position_filter}"
        )
    
    with col2:
        avg_cost = filtered_df['cost'].mean()
        st.metric(
            "Average Cost", 
            f"£{avg_cost:.1f}m",
            f"Range: £{filtered_df['cost'].min():.1f}-{filtered_df['cost'].max():.1f}m"
        )
    
    with col3:
        total_goals = filtered_df['goals_scored'].sum()
        st.metric(
            "Total Goals",
            f"{total_goals:,}",
            f"Avg: {filtered_df['goals_scored'].mean():.1f} per player"
        )
    
    with col4:
        total_assists = filtered_df['assists'].sum()
        st.metric(
            "Total Assists",
            f"{total_assists:,}",
            f"Avg: {filtered_df['assists'].mean():.1f} per player"
        )
    
    with col5:
        avg_ownership = filtered_df['selected_by_percent'].mean()
        st.metric(
            "Avg Ownership",
            f"{avg_ownership:.1f}%",
            f"Most owned: {filtered_df['selected_by_percent'].max():.1f}%"
        )

def create_footer():
    """Create the shared footer for all pages"""
    # Footer
    st.divider()
    
    # Developer info and photo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Check if developer photo exists (support multiple formats)
        photo_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        photo_path = None
        
        for ext in photo_extensions:
            potential_path = f"web_app/assets/images/developer{ext}"
            if os.path.exists(potential_path):
                photo_path = potential_path
                break
        
        if photo_path:
            # Display photo in circular frame with custom CSS
            st.markdown(
                """
                <style>
                .developer-photo {
                    display: flex;
                    justify-content: center;
                    margin-bottom: 1rem;
                }
                .developer-photo img {
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    object-fit: cover;
                    border: 4px solid #37003c;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    transition: transform 0.3s ease;
                }
                .developer-photo img:hover {
                    transform: scale(1.05);
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            # Use HTML to display the circular photo
            import base64
            with open(photo_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            
            st.markdown(
                f"""
                <div class="developer-photo">
                    <img src="data:image/jpeg;base64,{img_base64}" alt="Md Ataullah Khan Rifat">
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown(
            """
            <div style='text-align: center; color: #666;'>
                <p><strong>Developed by: Md Ataullah Khan Rifat</strong></p>
                <p>Built with ❤️ for FPL managers</p>
                <p><small>Data from official FPL API</small></p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Disclaimer
    st.markdown(
        """
        <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem;'>
            <h4 style='color: #37003c; margin-bottom: 0.5rem;'>📢 Disclaimer</h4>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>
                <strong>Educational Use Only:</strong> This application is developed for educational and research purposes only. 
                It is not intended for commercial use.
            </p>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>
                <strong>Data Source:</strong> All player data is sourced from the official Fantasy Premier League API. 
                This application is not affiliated with or endorsed by the Premier League or Fantasy Premier League.
            </p>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0;'>
                <strong>No Warranty:</strong> Predictions and recommendations are based on statistical models and should be used 
                as guidance only. The developer assumes no responsibility for Fantasy Premier League performance based on this tool.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def filter_available_players(players_df):
    """Silently filter out players who are not available for selection"""
    if players_df is None:
        return None
    
    # Remove players from relegated teams (teams that shouldn't be in Premier League)
    # Teams relegated from Premier League 2024-25 season (for 2025-26 season starting)
    # Southampton (20th), Leicester City (19th), Ipswich Town (18th) - all went down
    relegated_teams = ['Southampton', 'Leicester', 'Ipswich']
    relegated_mask = players_df['team'].str.contains('|'.join(relegated_teams), case=False, na=False)
    relegated_players = players_df[relegated_mask]
    if not relegated_players.empty:
        print(f"[Background] Filtered out {len(relegated_players)} players from relegated teams: {relegated_players['team'].unique().tolist()}")
    
    players_df = players_df[~relegated_mask].copy()
    
    # Remove players with high transfer risk (they may have moved to other leagues/teams)
    if 'transfer_risk' in players_df.columns:
        high_risk_players = players_df[players_df['transfer_risk'] == 'high']
        if not high_risk_players.empty:
            # Log the filtering for internal tracking (not shown to user)
            print(f"[Background] Filtered out {len(high_risk_players)} high-risk players")
        
        # Keep only low/medium risk players
        players_df = players_df[players_df['transfer_risk'] != 'high'].copy()
    
    # Remove players with data validation warnings
    if 'data_validation_warnings' in players_df.columns:
        flagged_players = players_df[players_df['data_validation_warnings'] == 1]
        if not flagged_players.empty:
            print(f"[Background] Filtered out {len(flagged_players)} flagged players")
        
        # Keep only players without validation warnings
        players_df = players_df[players_df['data_validation_warnings'] != 1].copy()
    
    # Remove players who are not selectable (if such data exists)
    # This could include injured players, suspended players, etc.
    if 'chance_of_playing_next_round' in players_df.columns:
        # Filter out players with very low chance of playing (less than 25%)
        unavailable_players = players_df[players_df['chance_of_playing_next_round'] < 25]
        if not unavailable_players.empty:
            print(f"[Background] Filtered out {len(unavailable_players)} likely unavailable players")
        
        players_df = players_df[players_df['chance_of_playing_next_round'] >= 25].copy()
    
    # Remove players with 0 minutes played and very low ownership (likely not active)
    inactive_players = players_df[
        (players_df['minutes'] == 0) & 
        (players_df['selected_by_percent'] < 0.1) &
        (players_df['total_points'] == 0)
    ]
    if not inactive_players.empty:
        print(f"[Background] Filtered out {len(inactive_players)} inactive players")
    
    players_df = players_df[~(
        (players_df['minutes'] == 0) & 
        (players_df['selected_by_percent'] < 0.1) &
        (players_df['total_points'] == 0)
    )].copy()
    
    return players_df

def main():
    """Main application function with page navigation"""
    
    # Load data first
    with st.spinner("Loading player data..."):
        players_df = load_player_data()
    
    if players_df is None:
        st.error("❌ Player data not found!")
        st.info("Please run the following command first: `python src/fetch_fpl_data.py`")
        st.stop()
    
    # Silently filter out unavailable players in the background
    players_df = filter_available_players(players_df)
    
    if players_df is None or len(players_df) == 0:
        st.error("❌ No available players found after filtering!")
        st.stop()
    
    # Page navigation in sidebar
    st.sidebar.markdown("## 🧭 Navigation")
    
    # Navigation buttons
    if st.sidebar.button("🚀 Squad Optimizer", use_container_width=True):
        st.session_state.current_page = 'optimizer'
    
    if st.sidebar.button("📊 Player Stats", use_container_width=True):
        st.session_state.current_page = 'stats'
    
    st.sidebar.divider()
    
    # Route to appropriate page
    if st.session_state.current_page == 'stats':
        create_stats_page(players_df)
    else:
        create_optimizer_page(players_df)
    
    # Shared Footer
    create_footer()

def create_optimizer_page(players_df):
    """Create the main optimizer page"""
    
    # Header
    st.markdown('<h1 class="main-header">⚽ FPL Squad Optimizer</h1>', unsafe_allow_html=True)
    st.markdown("**Optimize your Fantasy Premier League squad using machine learning and mathematical optimization**")
    
    st.success(f"✅ Loaded {len(players_df)} available players (filtered for quality and availability)")
    
    # Navigation button to Stats page
    col1, col2, col3, col4, col5 = st.columns(5)
    with col3:
        if st.button("📊 View Player Stats", key="goto_stats"):
            st.session_state.current_page = 'stats'
            st.rerun()
    
    st.divider()
    
    # Sidebar controls
    st.sidebar.header("⚙️ Optimization Settings")
    
    # Budget slider
    budget = st.sidebar.slider(
        "Squad Budget (£m)",
        min_value=80.0,
        max_value=120.0,
        value=100.0,
        step=0.5,
        help="Total budget for your 15-player squad"
    )
    
    # Additional filters
    st.sidebar.subheader("Advanced Settings")
    
    # Team filter
    all_teams = ['All Teams'] + sorted(players_df['team'].unique().tolist())
    excluded_teams = st.sidebar.multiselect(
        "Exclude Teams",
        options=all_teams[1:],  # Exclude 'All Teams' from options
        help="Select teams to exclude from optimization"
    )
    
    # FDR Settings
    fdr_settings = st.sidebar.expander("🌟 FDR (Fixture Difficulty) Settings")
    with fdr_settings:
        use_fdr = st.checkbox("Use FDR in optimization", value=True, 
                             help="Consider fixture difficulty when selecting players")
        if use_fdr:
            st.info("Lower FDR = easier fixtures = higher player value")
            fdr_attack_weight = st.slider("Attack FDR Impact", 0.0, 0.3, 0.1, 0.05, 
                                        help="How much attack FDR affects forwards/midfielders")
            fdr_defence_weight = st.slider("Defence FDR Impact", 0.0, 0.3, 0.1, 0.05,
                                         help="How much defence FDR affects defenders/goalkeepers")
            fdr_overall_weight = st.slider("Overall FDR Impact", 0.0, 0.2, 0.05, 0.01,
                                         help="General FDR impact on all players")
    
    # Team Position Limits
    team_position_limits = st.sidebar.expander("🏆 Team Position Limits")
    with team_position_limits:
        st.info("Prevent algorithm from selecting too many players of same position from one team")
        selected_limit_teams = st.multiselect("Select teams to limit", all_teams[1:])
        
        team_pos_limits = {}
        for team in selected_limit_teams:
            st.write(f"**{team} Limits:**")
            col1, col2 = st.columns(2)
            with col1:
                def_limit = st.number_input(f"Max Defenders", min_value=0, max_value=3, value=2, key=f"def_{team}")
                fwd_limit = st.number_input(f"Max Forwards", min_value=0, max_value=3, value=1, key=f"fwd_{team}")
            with col2:
                mid_limit = st.number_input(f"Max Midfielders", min_value=0, max_value=3, value=2, key=f"mid_{team}")
                gk_limit = st.number_input(f"Max Goalkeepers", min_value=0, max_value=2, value=1, key=f"gk_{team}")
            
            team_pos_limits[team] = {
                'Defender': def_limit,
                'Midfielder': mid_limit, 
                'Forward': fwd_limit,
                'Goalkeeper': gk_limit
            }
    
    # Team requirements
    team_requirements = st.sidebar.expander("Team Requirements (Optional)")
    with team_requirements:
        st.info("Set exact number of players from specific teams")
        all_teams = sorted(players_df['team'].unique().tolist()) if players_df is not None else []
        selected_teams = st.multiselect("Select teams", all_teams)
        
        team_reqs = {}
        for team in selected_teams:
            team_reqs[team] = st.number_input(f"{team} players", min_value=0, max_value=3, value=1, key=f"team_{team}")
    
    # Budget usage
    min_budget_usage = st.sidebar.slider(
        "Minimum Budget Usage (%)",
        min_value=85,
        max_value=100,
        value=99,
        step=1,
        help="Force optimizer to use at least this percentage of budget"
    ) / 100
    
    # Expensive player settings
    expensive_player_settings = st.sidebar.expander("💰 Expensive Player Strategy")
    with expensive_player_settings:
        expensive_threshold = st.slider(
            "Expensive Player Threshold (£m)",
            min_value=6.0,
            max_value=12.0,
            value=8.0,
            step=0.5,
            help="Players above this cost should prioritize starting XI"
        )
        
        very_expensive_threshold = st.slider(
            "Very Expensive Threshold (£m)", 
            min_value=8.0,
            max_value=15.0,
            value=10.0,
            step=0.5,
            help="Limit these premium players on bench"
        )
        
        max_expensive_bench = st.number_input(
            "Max Very Expensive on Bench",
            min_value=0,
            max_value=3,
            value=1,
            help="Maximum very expensive players allowed on bench"
        )
    
    # Optimize button
    if st.sidebar.button("🚀 Optimize Squad", type="primary"):
        
        # Filter data based on user selections
        filtered_df = players_df.copy()
        
        if excluded_teams:
            filtered_df = filtered_df[~filtered_df['team'].isin(excluded_teams)]
        
        with st.spinner("🤖 Finding optimal squad..."):
            # Load optimizer with enhanced settings
            optimizer = load_optimizer(budget)
            optimizer.min_budget_usage = min_budget_usage
            
            # Set FDR weights if enabled
            if use_fdr:
                optimizer.use_fdr = True
                optimizer.set_fdr_weights({
                    'attack': fdr_attack_weight,
                    'defence': fdr_defence_weight,
                    'overall': fdr_overall_weight
                })
            else:
                optimizer.use_fdr = False
            
            # Set team position limits
            if team_pos_limits:
                optimizer.set_team_position_limits(team_pos_limits)
            
            # Set expensive player thresholds
            optimizer.expensive_threshold = expensive_threshold
            optimizer.very_expensive_threshold = very_expensive_threshold
            optimizer.max_expensive_bench = max_expensive_bench
            
            # Set team requirements if any
            if team_reqs:
                optimizer.set_team_requirements(team_reqs)
            
            # Load model and predict points
            optimizer.load_model()
            filtered_df = optimizer.predict_points(filtered_df)
            
            # Run optimization
            results = optimizer.optimize_squad(filtered_df)
        
        # Display results
        if results['status'] == 'optimal':
            st.success("✅ Optimization completed successfully!")
            
            selected_players = results['selected_players']
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Cost",
                    f"£{results['total_cost']:.1f}m",
                    f"Budget: £{budget}m"
                )
            
            with col2:
                st.metric(
                    "Predicted Points",
                    f"{results['total_predicted_points']:.1f}",
                    f"Starting XI: {results.get('starting_predicted_points', 0):.1f}"
                )
            
            with col3:
                st.metric(
                    "Budget Usage",
                    f"{results.get('budget_usage_pct', 0):.1f}%",
                    f"£{results['remaining_budget']:.1f}m left"
                )
            
            with col4:
                avg_cost = results['total_cost'] / 15
                st.metric(
                    "Avg Player Cost",
                    f"£{avg_cost:.1f}m",
                    f"Max: £{selected_players['cost'].max():.1f}m"
                )
            
            # Tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔥 Starting XI", "📋 Full Squad", "📊 Analytics", "🏆 Top Players", "⚙️ Details"])
            
            with tab1:
                st.header("Starting XI (Most Important)")
                
                if 'starting_players' in results:
                    starting_players = results['starting_players']
                    
                    # Display starting formation
                    formation = f"GK: {len(starting_players[starting_players['position']=='Goalkeeper'])}-"
                    formation += f"DEF: {len(starting_players[starting_players['position']=='Defender'])}-"
                    formation += f"MID: {len(starting_players[starting_players['position']=='Midfielder'])}-"
                    formation += f"FWD: {len(starting_players[starting_players['position']=='Forward'])}"
                    
                    st.info(f"Formation: {formation} | Predicted Points: {results.get('starting_predicted_points', 0):.1f}")
                    
                    # Starting XI table
                    display_squad_table(starting_players)
                    
                    # Bench
                    if 'bench_players' in results and len(results['bench_players']) > 0:
                        st.subheader("Bench (4 players)")
                        bench_cols = st.columns([3, 2, 1, 1])
                        bench_cols[0].write("**Player**")
                        bench_cols[1].write("**Team**")
                        bench_cols[2].write("**Cost**")
                        bench_cols[3].write("**Role**")
                        
                        for _, player in results['bench_players'].iterrows():
                            bench_cols = st.columns([3, 2, 1, 1])
                            bench_cols[0].write(player['name'])
                            bench_cols[1].write(player['team'])
                            bench_cols[2].write(f"£{player['cost']:.1f}m")
                            bench_cols[3].write("Bench")
                else:
                    st.info("Starting XI breakdown not available. Showing top 11 players.")
                    top_11 = selected_players.head(11)
                    display_squad_table(top_11)
            
            with tab2:
                st.header("Complete Squad (15 Players)")
                display_squad_table(selected_players)
                
                # Download button
                csv = selected_players.to_csv(index=False)
                st.download_button(
                    label="📥 Download Squad CSV",
                    data=csv,
                    file_name=f"fpl_optimal_squad_budget_{budget}.csv",
                    mime="text/csv"
                )
            
            with tab3:
                st.header("Squad Analytics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Position pie chart
                    fig1 = create_position_pie_chart(selected_players)
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Team distribution
                    fig2 = create_team_distribution_chart(selected_players)
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Cost vs Points scatter
                fig3 = create_cost_vs_points_scatter(selected_players)
                st.plotly_chart(fig3, use_container_width=True)
            
            with tab4:
                st.header("Top Players by Predicted Points")
                
                # Top players table
                top_players = selected_players.nlargest(10, 'predicted_points')[
                    ['name', 'position', 'team', 'cost', 'form', 'predicted_points', 'total_points', 'selected_by_percent']
                ]
                
                st.dataframe(
                    top_players,
                    column_config={
                        "name": "Player",
                        "position": "Position",
                        "team": "Team",
                        "cost": st.column_config.NumberColumn("Cost", format="£%.1f"),
                        "form": st.column_config.NumberColumn("Form", format="%.1f"),
                        "predicted_points": st.column_config.NumberColumn("Predicted Points", format="%.1f"),
                        "total_points": st.column_config.NumberColumn("Season Points", format="%d"),
                        "selected_by_percent": st.column_config.NumberColumn("Ownership %", format="%.1f%%")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            
            with tab5:
                st.header("Optimization Details")
                
                # Settings applied
                st.subheader("Settings Applied")
                settings_data = [
                    ['Budget', f'£{budget}m'],
                    ['Min Budget Usage', f'{min_budget_usage*100:.0f}%'],
                    ['FDR Enabled', 'Yes' if use_fdr else 'No'],
                    ['Team Requirements', str(team_reqs) if team_reqs else 'None'],
                    ['Max per Team', f'{3} players']
                ]
                
                if use_fdr:
                    settings_data.extend([
                        ['FDR Attack Weight', f'{fdr_attack_weight:.2f}'],
                        ['FDR Defence Weight', f'{fdr_defence_weight:.2f}'],
                        ['FDR Overall Weight', f'{fdr_overall_weight:.2f}']
                    ])
                
                if team_pos_limits:
                    settings_data.append(['Team Position Limits', f'{len(team_pos_limits)} teams'])
                
                # Add expensive player settings
                settings_data.extend([
                    ['Expensive Player Threshold', f'£{expensive_threshold}m'],
                    ['Very Expensive Threshold', f'£{very_expensive_threshold}m'],
                    ['Max Expensive on Bench', str(max_expensive_bench)]
                ])
                
                settings_df = pd.DataFrame(settings_data, columns=['Setting', 'Value'])
                st.dataframe(settings_df, hide_index=True, use_container_width=True)
                
                # Constraints summary
                st.subheader("Constraints Applied")
                constraints_df = pd.DataFrame({
                    'Constraint': [
                        'Total Budget',
                        'Squad Size',
                        'Goalkeepers',
                        'Defenders',
                        'Midfielders',
                        'Forwards',
                        'Max per Team'
                    ],
                    'Requirement': [
                        f'≤ £{budget}m',
                        '= 15 players',
                        '= 2 players',
                        '= 5 players',
                        '= 5 players',
                        '= 3 players',
                        '≤ 3 players'
                    ],
                    'Actual': [
                        f'£{results["total_cost"]:.1f}m',
                        f'{len(selected_players)} players',
                        f'{results["position_breakdown"].get("Goalkeeper", 0)} players',
                        f'{results["position_breakdown"].get("Defender", 0)} players',
                        f'{results["position_breakdown"].get("Midfielder", 0)} players',
                        f'{results["position_breakdown"].get("Forward", 0)} players',
                        f'{max(results["team_breakdown"].values())} players'
                    ]
                })
                
                st.dataframe(constraints_df, hide_index=True, use_container_width=True)
                
                # Team breakdown
                st.subheader("Team Distribution")
                team_df = pd.DataFrame(list(results['team_breakdown'].items()), 
                                     columns=['Team', 'Players'])
                team_df = team_df.sort_values('Players', ascending=False)
                st.dataframe(team_df, hide_index=True, use_container_width=True)
        
        else:
            st.error("❌ Optimization failed!")
            st.error(results.get('message', 'No feasible solution found'))
            st.info("Try adjusting your budget or constraints.")
    
    # Footer
    st.divider()
    
    # Developer info and photo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Check if developer photo exists (support multiple formats)
        photo_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        photo_path = None
        
        for ext in photo_extensions:
            potential_path = f"web_app/assets/images/developer{ext}"
            if os.path.exists(potential_path):
                photo_path = potential_path
                break
        
        if photo_path:
            # Display photo in circular frame with custom CSS
            st.markdown(
                """
                <style>
                .developer-photo {
                    display: flex;
                    justify-content: center;
                    margin-bottom: 1rem;
                }
                .developer-photo img {
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    object-fit: cover;
                    border: 4px solid #37003c;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    transition: transform 0.3s ease;
                }
                .developer-photo img:hover {
                    transform: scale(1.05);
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            # Use HTML to display the circular photo
            import base64
            with open(photo_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            
            st.markdown(
                f"""
                <div class="developer-photo">
                    <img src="data:image/jpeg;base64,{img_base64}" alt="Md Ataullah Khan Rifat">
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown(
            """
            <div style='text-align: center; color: #666;'>
                <p><strong>Developed by: Md Ataullah Khan Rifat</strong></p>
                <p>Built with ❤️ for FPL managers</p>
                <p><small>Data from official FPL API</small></p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Disclaimer
    st.markdown(
        """
        <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem;'>
            <h4 style='color: #37003c; margin-bottom: 0.5rem;'>📢 Disclaimer</h4>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>
                <strong>Educational Use Only:</strong> This application is developed for educational and research purposes only. 
                It is not intended for commercial use.
            </p>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>
                <strong>Data Source:</strong> All player data is sourced from the official Fantasy Premier League API. 
                This application is not affiliated with or endorsed by the Premier League or Fantasy Premier League.
            </p>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0;'>
                <strong>No Warranty:</strong> Predictions and recommendations are based on statistical models and should be used 
                as guidance only. The developer assumes no responsibility for Fantasy Premier League performance based on this tool.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Run the main application
if __name__ == "__main__":
    main()
