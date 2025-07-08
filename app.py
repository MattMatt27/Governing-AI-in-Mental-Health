#!/usr/bin/env python3
"""
Mental Health AI Bill Tracker - Flask Application
A complete web application for tracking mental health AI legislation
"""

from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration with better error handling
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set!")
    print("Please set it in your .env file for local development or in Railway's environment variables.")
    sys.exit(1)

# Tag definitions
TAG_DEFINITIONS = {
    'civil_penalties': {
        'name': 'Civil Penalties',
        'definition': 'Applies any kind of civil penalty to violators (e.g., non-criminal penalties such as system suspension, civil fines, creation of private right-of-action to sue, profit disgorgement, suspension of noncompliant systems, punitive monitoring, or application of a separate civil enforcement statute).'
    },
    'criminal_penalties': {
        'name': 'Criminal Penalties',
        'definition': 'Applies any kind of criminal penalty to violators (e.g., criminal fines, incarceration, misdemeanor/felony designations).'
    },
    'licensing_board_oversight': {
        'name': 'Licensing Board Oversight',
        'definition': 'Applies any kind of oversight by state professional licensing boards (e.g., requiring board approval of MH-AI systems used in diagnosis/treatment or allowing boards to discipline individuals or systems).'
    },
    'disclosure_consent': {
        'name': 'Disclosure/Consent',
        'definition': 'Implements any requirement to disclose use or features of the AI system (including disclaimers) and/or consent to the use of such systems/features or the ability to revoke consent.'
    },
    'discrimination_bias': {
        'name': 'Discrimination/Bias',
        'definition': 'Implements any requirement regarding discrimination, bias, or fairness.'
    },
    'risk_classification': {
        'name': 'Risk Classification',
        'definition': 'Implements or defines the scope of the law by a risk classification system (e.g., "high risk" AI system, consequential decisions, and similar frameworks).'
    },
    'data_protection': {
        'name': 'Data Protection',
        'definition': 'Implements any requirements for data privacy, data security, or data retention/deletion (e.g., encryption requirements, secure storage, or data purging policies).'
    },
    'prescribing': {
        'name': 'Prescribing',
        'definition': 'Applies any requirements or waivers regarding prescriptions.'
    },
    'practitioner_responsibilities': {
        'name': 'Practitioner Responsibilities',
        'definition': 'Applies any kind of requirements on practitioners—or waivers or exemptions—related to their use of AI systems.'
    },
    'monitoring': {
        'name': 'Monitoring',
        'definition': 'Applies any kind of monitoring requirements for MH-AI (e.g., live supervision, submission to audits/documentation processes, generation of reports, or post-market surveillance).'
    },
    'research': {
        'name': 'Research',
        'definition': 'Pertains to or would affect mental health research (e.g., data collection, consent requirements, ethical guidelines, exemptions for legitimate research use, etc.)'
    },
    'consumer_protection': {
        'name': 'Consumer Protection',
        'definition': 'Provisions concerning fraudulent, manipulative, or deceptive use of MH-AI systems, including in advertising.'
    },
    'payments_insurance': {
        'name': 'Payments/Insurance',
        'definition': 'Regulations on insurance coverage, reimbursement, and payment models.'
    },
    'human_in_the_loop': {
        'name': 'Human-in-the-Loop',
        'definition': 'Explicitly requires a human to monitor, approve, or participate in an essential part of the provision of the MH-AI service.'
    },
    'pre_market_review': {
        'name': 'Pre-Market Review',
        'definition': 'Implements requirements for any level of regulatory review prior to the AI product being offered/implemented (e.g., state commission approval, FDA approval, submission of risk assessments, etc.).'
    },
    'post_market_review': {
        'name': 'Post-Market Review',
        'definition': 'Implements requirements for any level of scheduled/routine review after the AI product has been marketed/implemented (e.g., post-market surveillance, auditing, risk assessments, efficacy reviews, etc.), subject to regulatory oversight.'
    },
    'transparency': {
        'name': 'Transparency',
        'definition': 'Implements requirements involving public or patient rights to access AI system data (e.g., requests to obtain data, public inventories of AI systems, publication or transparency requirements).'
    },
    'opt_out': {
        'name': 'Opt Out',
        'definition': 'Provides for the ability to opt out of AI services in favor of receiving equivalent human-delivered health services.'
    },
    'pilot_sandbox': {
        'name': 'Pilot/Sandbox',
        'definition': 'Provides for regulatory pilot programs or sandbox systems, allowing AI products to be tested and receive feedback from regulators prior to full marketing.'
    },
    'malpractice': {
        'name': 'Malpractice/Liability',
        'definition': 'Pertains to medical malpractice involving AI, including liability allocation for AI-related harm (e.g., standards of evidence, assigning responsibility to deployers, developers, practitioners, or manufacturers, liability shields or limitations, use of MH-AI records and data in litigation, etc.).'
    },
    'event_reporting': {
        'name': 'Event Reporting',
        'definition': 'Creates a system for reporting adverse events, near misses, or other safety events involving MH-AI.'
    },
    'vulnerable_populations': {
        'name': 'Vulnerable Populations',
        'definition': 'Creates any responsibilities related to vulnerable populations (e.g., elderly, children, disabled, foreign-language speakers, etc.), such as mandated reporting requirements, accessibility requirements, or parental controls.'
    },
    'meta_biometric_data': {
        'name': 'Meta/Biometric Data',
        'definition': 'Regulates biometric data, behavioral data, or metadata used by MH-AI systems.'
    },
    'special_purpose_entities': {
        'name': 'Special Purpose Entities',
        'definition': 'Creates or assigns committees, subcommittees, task forces, or similar special-purpose bodies pertaining to MH-AI.'
    },
    'safety_standards': {
        'name': 'Safety Standards',
        'definition': 'Pertains to safety standards for MH-AI (e.g., human overrides, emergency protocols, or prohibitions on high-risk uses) or safety-based exceptions to other requirements (e.g., bypassing procedures when delays risk harm, allowing immediate protective actions).'
    }
}

# Taxonomy definitions
TAXONOMY_DEFINITIONS = {
    'E': {
        'name': 'Explicit',
        'definition': 'Bills that explicitly reference mental health, behavioral health, psychotherapy, or related services in the context of AI development, regulation, or application.',
        'inclusion': 'The bill directly names mental health uses of AI, specific clinical applications, or mental health contexts as targets of regulation, policy, or oversight.'
    },
    'SR': {
        'name': 'Substantively Relevant',
        'definition': 'Bills that govern MH-AI in ways that have direct, foreseeable implications for mental health services or stakeholders, even if mental health is not explicitly or substantively discussed in the bill\'s text.',
        'inclusion': 'The bill regulates MH-AI in a way that predictably impacts mental health uses, delivery, or providers, regardless of whether mental health is explicitly mentioned.'
    },
    'II': {
        'name': 'Incidentally Implicative',
        'definition': 'Bills that are broadly written and might include MH-AI, but only in a general or indirect way. Clinical impact is uncertain or minimal.',
        'inclusion': 'MH-AI falls or could fall under the bill\'s scope, but direct mechanisms or practical effects at the clinical level are not apparent or minimal.'
    },
    'CB': {
        'name': 'Companion Bill',
        'definition': 'Bills that are companion legislation to other bills in the dataset.',
        'inclusion': 'The bill is a companion to another bill, typically in a different chamber of the legislature.'
    },
    'NR': {
        'name': 'Not Relevant',
        'definition': 'Bills with no meaningful relationship to MH-AI services, even under expansive interpretations.',
        'inclusion': 'The bill does not touch on mental health services.'
    }
}

def get_db_connection():
    """Create database connection with error handling"""
    try:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        raise

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', 
                         tag_definitions=TAG_DEFINITIONS,
                         taxonomy_definitions=TAXONOMY_DEFINITIONS)

@app.route('/api/bills')
def get_bills():
    """API endpoint to get bills with filters"""
    try:
        # Get query parameters
        state = request.args.get('state')
        taxonomy_code = request.args.get('taxonomy_code')
        search = request.args.get('search', '')
        hide_nr = request.args.get('hide_nr', 'true').lower() == 'true'
        
        # Get selected tags
        selected_tags = request.args.getlist('tags[]')
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if state and state != 'all':
            where_conditions.append("state = %s")
            params.append(state)
        
        if taxonomy_code and taxonomy_code != 'all':
            where_conditions.append("taxonomy_code = %s")
            params.append(taxonomy_code)
        
        if hide_nr:
            where_conditions.append("taxonomy_code != 'NR'")
        
        if search:
            where_conditions.append("(bill ILIKE %s OR state ILIKE %s)")
            params.extend([f'%{search}%', f'%{search}%'])
        
        # Add tag filters
        for tag in selected_tags:
            if tag in TAG_DEFINITIONS:
                where_conditions.append(f"{tag} = true")
        
        # Build query
        query = """
            SELECT *,
            (civil_penalties::int + criminal_penalties::int + licensing_board_oversight::int + 
             disclosure_consent::int + discrimination_bias::int + risk_classification::int + 
             data_protection::int + prescribing::int + practitioner_responsibilities::int + 
             monitoring::int + research::int + consumer_protection::int + 
             payments_insurance::int + human_in_the_loop::int + pre_market_review::int + 
             post_market_review::int + transparency::int + opt_out::int + 
             pilot_sandbox::int + malpractice::int + event_reporting::int + 
             vulnerable_populations::int + meta_biometric_data::int + 
             special_purpose_entities::int + safety_standards::int) as tag_count
            FROM bill_data
        """
        
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
        
        query += " ORDER BY state, bill"
        
        # Execute query
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        bills = cur.fetchall()
        cur.close()
        conn.close()
        
        # Process bills for frontend
        for bill in bills:
            # Add legiscan link
            bill['link'] = f"https://legiscan.com/{bill['state']}/bill/{bill['bill']}/2025"
            
            # Add active tags list
            bill['active_tags'] = []
            for tag_key, tag_info in TAG_DEFINITIONS.items():
                if bill.get(tag_key, False):
                    bill['active_tags'].append(tag_info['name'])
        
        return jsonify(bills)
    
    except Exception as e:
        print(f"Error in get_bills: {e}")
        return jsonify({'error': 'Failed to fetch bills'}), 500

@app.route('/api/stats')
def get_stats():
    """API endpoint to get statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get total bills
        cur.execute("SELECT COUNT(*) as total FROM bill_data")
        total_bills = cur.fetchone()['total']
        
        # Get taxonomy summary
        cur.execute("""
            SELECT taxonomy_code, COUNT(*) as count 
            FROM bill_data 
            GROUP BY taxonomy_code 
            ORDER BY taxonomy_code
        """)
        taxonomy_summary = cur.fetchall()
        
        # Get state summary
        cur.execute("""
            SELECT state, COUNT(*) as count 
            FROM bill_data 
            GROUP BY state 
            ORDER BY count DESC
            LIMIT 10
        """)
        state_summary = cur.fetchall()
        
        # Get tag statistics
        tag_stats = []
        for tag_key, tag_info in TAG_DEFINITIONS.items():
            cur.execute(f"SELECT COUNT(*) as count FROM bill_data WHERE {tag_key} = true")
            count = cur.fetchone()['count']
            tag_stats.append({
                'name': tag_info['name'],
                'count': count
            })
        
        # Sort tag stats by count
        tag_stats.sort(key=lambda x: x['count'], reverse=True)
        
        cur.close()
        conn.close()
        
        return jsonify({
            'total_bills': total_bills,
            'taxonomy_summary': taxonomy_summary,
            'state_summary': state_summary,
            'tag_stats': tag_stats
        })
    
    except Exception as e:
        print(f"Error in get_stats: {e}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@app.route('/api/states')
def get_states():
    """Get list of all states"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT state FROM bill_data ORDER BY state")
        states = [row['state'] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(states)
    
    except Exception as e:
        print(f"Error in get_states: {e}")
        return jsonify({'error': 'Failed to fetch states'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    try:
        # Test database connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

if __name__ == '__main__':
    # Use PORT from environment for Railway deployment
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)