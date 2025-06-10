"""
Step 3: Generate Variations for MultiPromptify 2.0
"""
import pandas as pd
import streamlit as st
import json
import time
import os
from dotenv import load_dotenv
from src.multipromptify import MultiPromptify
from src.utils.constants import DEFAULT_MODEL

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("TOGETHER_API_KEY")


def render():
    """Render the variations generation interface"""
    if not st.session_state.get('template_ready', False):
        st.error("⚠️ Please complete the template setup first (Step 2)")
        if st.button("← Go to Step 2"):
            st.session_state.page = 2
            st.rerun()
        return
    
    # Enhanced header with better styling
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; text-align: center;">
            ⚡ Step 3: Generate Variations
        </h1>
        <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;">
            Configure settings and generate your prompt variations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get data and template
    df = st.session_state.uploaded_data
    template = st.session_state.selected_template
    template_name = st.session_state.get('template_name', 'Custom Template')
    
    # Display current setup
    display_current_setup(df, template, template_name)
    
    # Add visual separator
    st.markdown("---")
    
    # Generation configuration
    configure_generation()
    
    # Add visual separator
    st.markdown("---")
    
    # Generate variations
    generate_variations_interface()


def display_current_setup(df, template, template_name):
    """Display the current data and template setup with enhanced cards"""
    st.subheader("📋 Current Setup Overview")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("**📊 Data Summary**")
        
        # Metrics in a more visual way
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("📝 Rows", len(df))
        with metric_col2:
            st.metric("🗂️ Columns", len(df.columns))
        
        st.markdown("**📋 Available Columns:**")
        columns_text = ", ".join(df.columns.tolist())
        st.markdown(f'<div style="background: #e9ecef; padding: 0.5rem; border-radius: 5px; font-family: monospace;">{columns_text}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**📝 Template: {template_name}**")
        st.code(template, language="text")


def configure_generation():
    """Configure generation settings with enhanced visual design"""
    st.subheader("⚙️ Generation Configuration")
    
    # Main settings in cards
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("**🔢 Quantity Settings**")
        
        # Max variations setting
        max_variations = st.number_input(
            "🎯 Maximum variations to generate",
            min_value=1,
            max_value=1000,
            value=st.session_state.get('max_variations', 50),
            help="Total number of prompt variations to generate across all data rows"
        )
        st.session_state.max_variations = max_variations
        
        # Max rows setting
        df = st.session_state.uploaded_data
        max_rows = st.number_input(
            "📊 Maximum rows from data to use",
            min_value=1,
            max_value=len(df),
            value=st.session_state.get('max_rows', len(df)),
            help=f"Use only the first N rows from your data (total: {len(df)} rows)"
        )
        st.session_state.max_rows = max_rows
        
        # Variations per field
        variations_per_field = st.number_input(
            "🔄 Variations per field",
            min_value=1,
            max_value=10,
            value=st.session_state.get('variations_per_field', 3),
            help="Number of variations to generate for each field with variation annotations"
        )
        st.session_state.variations_per_field = variations_per_field
    
    with col2:
        st.markdown("**✍️ Content Settings**")
        
        # Instruction input
        instruction = st.text_input(
            "📝 Global Instruction",
            placeholder=st.session_state.get('preview_instruction', "Please complete the following task"),
            help="Static instruction text that will be used across all prompts"
        )
        if not instruction:
            instruction = st.session_state.get('preview_instruction', "Please complete the following task")
        st.session_state.generation_instruction = instruction
        
        # Random seed for reproducibility
        st.markdown("**🎲 Reproducibility Options**")
        use_seed = st.checkbox("🔒 Use random seed for reproducible results")
        if use_seed:
            seed = st.number_input("🌱 Random seed", min_value=0, value=42)
            if seed is None:
                seed = 42
            st.session_state.random_seed = seed
        else:
            st.session_state.random_seed = None
    
    # Check if template uses paraphrase variations
    template = st.session_state.get('selected_template', '')
    needs_api_key = ':paraphrase' in template
    
    if needs_api_key:
        # Enhanced API Configuration in sidebar
        with st.sidebar:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
                <h3 style="color: white; margin: 0;">🔑 API Configuration</h3>
                <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">Required for advanced variations</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("🤖 Your template uses paraphrase variations which require an API key.")
            
            # Platform selection
            platform = st.selectbox(
                "🌐 Platform", 
                ["TogetherAI", "OpenAI"], 
                index=0,
                help="Choose the AI platform for paraphrase generation"
            )
            st.session_state.api_platform = platform
            
            # Model name with default value directly in the text box
            default_model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
            current_model = st.session_state.get('model_name', default_model)
            model_name = st.text_input(
                "🧠 Model Name", 
                value=current_model,
                help="Name of the model to use for paraphrase generation"
            )
            st.session_state.model_name = model_name
            
            # API Key input
            api_key = st.text_input(
                f"🔐 API Key for {platform}",
                type="password",
                value=st.session_state.get('api_key', API_KEY or ''),
                help=f"Required for generating paraphrase variations using {platform}"
            )
            # Use environment API key as default if nothing entered
            st.session_state.api_key = api_key
            
            if not api_key:
                st.warning("⚠️ API key is required for paraphrase variations. Generation may not work without it.")
    else:
        # Clear API key if not needed
        for key in ['api_key', 'api_platform', 'model_name']:
            if key in st.session_state:
                del st.session_state[key]
    
    # Remove the old few-shot configuration interface
    st.session_state.generation_few_shot = None


def generate_variations_interface():
    """Enhanced interface for generating variations"""
    st.subheader("🚀 Generate Variations")

    # Estimation in a compact info box
    df = st.session_state.uploaded_data
    max_variations = st.session_state.get('max_variations', 50)
    variations_per_field = st.session_state.get('variations_per_field', 3)
    max_rows = st.session_state.get('max_rows', len(df))
    
    # Use only the selected number of rows for estimation
    effective_rows = min(max_rows, len(df))
    
    # Estimate total variations
    mp = MultiPromptify()
    try:
        variation_fields = mp.parse_template(st.session_state.selected_template)
        num_variation_fields = len([f for f, v in variation_fields.items() if v is not None])
        
        if num_variation_fields > 0:
            estimated_per_row = min(variations_per_field ** num_variation_fields, max_variations // effective_rows)
            estimated_total = min(estimated_per_row * effective_rows, max_variations)
        else:
            estimated_total = effective_rows  # No variations, just one prompt per row
        
        # Compact estimation display
        st.info(f"📊 **Generation Estimate:** ~{estimated_total:,} variations • {estimated_total//effective_rows if effective_rows > 0 else 0} per row • from {effective_rows:,} rows")
    
    except Exception as e:
        st.warning(f"❌ Could not estimate variations: {str(e)}")
    
    # Enhanced generation button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Generate All Variations", type="primary", use_container_width=True):
            generate_all_variations()
    
    # Show existing results if available
    if st.session_state.get('variations_generated', False):
        display_generation_results()


def generate_all_variations():
    """Generate all variations with progress tracking"""
    
    # Create an expandable progress container
    with st.expander("📊 Generation Progress & Details", expanded=True):
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🔄 Generation in Progress...")
            
            # Progress bar and status
            progress_bar = st.progress(0)
            status_text = st.empty()
            details_text = st.empty()
            
            try:
                start_time = time.time()
                
                # Step 1: Initialize
                status_text.text("🔄 Step 1/5: Initializing MultiPromptify...")
                details_text.info("Setting up the generation engine with your configuration")
                progress_bar.progress(0.1)
                
                mp = MultiPromptify(max_variations=st.session_state.max_variations)
                
                # Set random seed if specified
                if st.session_state.get('random_seed') is not None:
                    import random
                    random.seed(st.session_state.random_seed)
                    details_text.info(f"🌱 Random seed set to: {st.session_state.random_seed}")
                
                # Step 2: Prepare data
                status_text.text("📊 Step 2/5: Preparing data...")
                progress_bar.progress(0.2)
                
                df = st.session_state.uploaded_data
                max_rows = st.session_state.get('max_rows', len(df))
                
                # Limit data to selected number of rows
                if max_rows < len(df):
                    df = df.head(max_rows)
                    details_text.info(f"📊 Using first {max_rows} rows out of {len(st.session_state.uploaded_data)} total rows")
                else:
                    details_text.info(f"📊 Using all {len(df)} rows from your data")
                
                # Step 3: Configure parameters
                status_text.text("⚙️ Step 3/5: Configuring generation parameters...")
                progress_bar.progress(0.3)
                
                template = st.session_state.selected_template
                instruction = st.session_state.get('generation_instruction')
                variations_per_field = st.session_state.get('variations_per_field', 3)
                api_key = st.session_state.get('api_key')
                
                # Process few-shot examples - now handled via template syntax
                # No manual processing needed as few-shot is defined in template
                
                # Show configuration details
                config_details = []
                if instruction:
                    config_details.append(f"✍️ Instruction: {instruction[:50]}...")
                config_details.append(f"🔄 Variations per field: {variations_per_field}")
                if api_key:
                    config_details.append("🔑 API key configured for advanced variations")
                
                details_text.info(" | ".join(config_details))
                
                # Step 4: Generate variations
                status_text.text("⚡ Step 4/5: Generating variations...")
                details_text.warning("🤖 AI is working hard to create your prompt variations...")
                progress_bar.progress(0.4)
                
                variations = mp.generate_variations(
                    template=template,
                    data=df,
                    instruction=instruction,
                    variations_per_field=variations_per_field,
                    api_key=api_key
                )
                
                # Step 5: Computing statistics
                status_text.text("📈 Step 5/5: Computing statistics...")
                progress_bar.progress(0.8)
                details_text.info(f"✨ Generated {len(variations)} variations successfully!")
                
                stats = mp.get_stats(variations)
                
                # Complete
                progress_bar.progress(1.0)
                end_time = time.time()
                generation_time = end_time - start_time
                
                # Store results
                st.session_state.generated_variations = variations
                st.session_state.generation_stats = stats
                st.session_state.generation_time = generation_time
                st.session_state.variations_generated = True
                
                # Final success message
                status_text.text("✅ Generation Complete!")
                details_text.success(f"🎉 Successfully generated {len(variations)} variations in {generation_time:.1f} seconds!")
                
                # Add summary statistics
                st.markdown("#### 📊 Quick Summary:")
                summary_col1, summary_col2, summary_col3 = st.columns(3)
                
                with summary_col1:
                    st.metric("Total Variations", len(variations))
                with summary_col2:
                    st.metric("Processing Time", f"{generation_time:.1f}s")
                with summary_col3:
                    avg_per_row = len(variations) / len(df) if len(df) > 0 else 0
                    st.metric("Avg per Row", f"{avg_per_row:.1f}")
                
                # Auto-scroll to results after a short delay
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                # Error handling with details
                status_text.text("❌ Generation Failed")
                details_text.error(f"❌ Error: {str(e)}")
                
                st.error(f"❌ Error generating variations: {str(e)}")
                import traceback
                with st.expander("🔍 Debug Information"):
                    st.code(traceback.format_exc())


def display_generation_results():
    """Enhanced display of variation generation results"""
    if not st.session_state.get('variations_generated', False):
        return
    
    # Success header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); 
                padding: 2rem; border-radius: 10px; margin: 2rem 0;">
        <h2 style="color: white; margin: 0; text-align: center;">🎉 Generation Complete!</h2>
        <p style="color: rgba(255,255,255,0.9); text-align: center; margin: 0.5rem 0 0 0;">
            Your prompt variations have been successfully generated
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    variations = st.session_state.generated_variations
    stats = st.session_state.generation_stats
    generation_time = st.session_state.generation_time
    
    # Enhanced summary metrics with cards
    st.markdown("### 📊 Generation Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 2rem;">{}</h2>
            <p style="margin: 0; opacity: 0.8;">Total Variations</p>
        </div>
        """.format(len(variations)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); 
                    padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 2rem;">{}</h2>
            <p style="margin: 0; opacity: 0.8;">Original Rows</p>
        </div>
        """.format(stats.get('original_rows', 0)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 2rem;">{:.1f}</h2>
            <p style="margin: 0; opacity: 0.8;">Avg per Row</p>
        </div>
        """.format(stats.get('avg_variations_per_row', 0)), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                    padding: 1.5rem; border-radius: 10px; text-align: center; color: #333;">
            <h2 style="margin: 0; font-size: 2rem;">{:.1f}s</h2>
            <p style="margin: 0; opacity: 0.7;">Generation Time</p>
        </div>
        """.format(generation_time), unsafe_allow_html=True)
    
    # Detailed statistics in an expandable card

    # Sample variations preview with enhanced cards
    st.markdown("---")
    st.markdown("### 👀 Sample Variations Preview")
    num_preview = min(5, len(variations))
    
    for i in range(num_preview):
        with st.expander(f"🔍 Sample Variation {i+1}", expanded=(i == 0)):
            variation = variations[i]
            
            # Prompt display
            st.markdown("**Generated Prompt:**")
            st.markdown("""
            <div style="background: #f1f3f4; padding: 1rem; border-radius: 8px; border-left: 4px solid #4285f4;">
            """, unsafe_allow_html=True)
            st.code(variation['prompt'], language="text")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Metadata display
            st.markdown("**📋 Metadata:**")
            metadata = {
                'original_row_index': variation.get('original_row_index'),
                'field_values': variation.get('field_values'),
                'template': variation.get('template')
            }
            st.json(metadata)
    
    if len(variations) > num_preview:
        st.info(f"💡 ... and {len(variations) - num_preview} more variations (view all in Step 4)")
    
    # Enhanced download section
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #e3f2fd; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #2196f3; margin: 2rem 0;">
        <h3 style="color: #1976d2; margin-top: 0;">💾 Download Your Results</h3>
        <p style="margin-bottom: 0; color: #0d47a1;">Choose your preferred format to download the generated variations</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON download with enhanced styling
        st.markdown("""
        <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; margin-bottom: 1rem;">
            <h4 style="color: #ff9800; margin: 0;">📋 JSON Format</h4>
            <p style="margin: 0.5rem 0; color: #666; font-size: 0.9rem;">Complete data with metadata</p>
        </div>
        """, unsafe_allow_html=True)
        
        json_data = json.dumps(variations, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name="prompt_variations.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # CSV download with enhanced styling
        st.markdown("""
        <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; margin-bottom: 1rem;">
            <h4 style="color: #4caf50; margin: 0;">📊 CSV Format</h4>
            <p style="margin: 0.5rem 0; color: #666; font-size: 0.9rem;">Spreadsheet compatible</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Flatten for CSV
        flattened = []
        for var in variations:
            flat_var = {
                'prompt': var['prompt'],
                'original_row_index': var.get('original_row_index', ''),
                'variation_count': var.get('variation_count', ''),
            }
            # Add field values
            for key, value in var.get('field_values', {}).items():
                flat_var[f'field_{key}'] = value
            flattened.append(flat_var)
        
        csv_df = pd.DataFrame(flattened)
        csv_data = csv_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="prompt_variations.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        # Text download with enhanced styling
        st.markdown("""
        <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; margin-bottom: 1rem;">
            <h4 style="color: #9c27b0; margin: 0;">📝 Text Format</h4>
            <p style="margin: 0.5rem 0; color: #666; font-size: 0.9rem;">Plain text prompts only</p>
        </div>
        """, unsafe_allow_html=True)
        
        text_data = "\n\n--- VARIATION ---\n\n".join([var['prompt'] for var in variations])
        
        st.download_button(
            label="📥 Download TXT",
            data=text_data,
            file_name="prompt_variations.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Enhanced continue button
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Continue to View Results →", type="primary", use_container_width=True):
            st.session_state.page = 4
            st.rerun() 