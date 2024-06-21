import sys
import subprocess

def extract_atom_lines(input_pdb, output_pdb):
    try:
        with open(input_pdb, 'r') as infile, open(output_pdb, 'w') as outfile:
            for line in infile:
                if line.startswith("ATOM"):
                    outfile.write(line)
        print(f"ATOM lines have been successfully extracted to {output_pdb}")
    except Exception as e:
        print(f"An error occurred: {e}")

def generate_files(pdb_file1, pdb_file2, pseudo_file, com_file):
    try:
        with open(pdb_file1, 'r') as infile1, open(pdb_file2, 'r') as infile2:
            with open(pseudo_file, 'w') as pseudo_out, open(com_file, 'w') as com_out:
                for line1, line2 in zip(infile1, infile2):
                    if line1.startswith("ATOM") and line2.startswith("ATOM"):
                        atom_info1 = line1[12:16].strip()  # Atom name
                        residue_info1 = line1[17:20].strip()  # Residue name
                        chain_id1 = line1[21].strip()  # Chain identifier
                        residue_seq1 = line1[22:26].strip()  # Residue sequence number

                        atom_info2 = line2[12:16].strip()  # Atom name
                        residue_info2 = line2[17:20].strip()  # Residue name
                        chain_id2 = line2[21].strip()  # Chain identifier
                        residue_seq2 = line2[22:26].strip()  # Residue sequence number

                        # Write to Pseudobond.pd file
                        pseudo_out.write(f"#0:{residue_seq1}.{chain_id1}@{atom_info1} #1:{residue_seq2}.{chain_id2}@{atom_info2}\n")

                        # Write to .com file
                        com_out.write(f"distance #0:{residue_seq1}.{chain_id1}@{atom_info1} #1:{residue_seq2}.{chain_id2}@{atom_info2}\n")
        print(f"Pseudobond and .com files have been successfully generated to {pseudo_file} and {com_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

def run_chimera(pdb_file1, pdb_file2, com_file, output_txt='distances.txt'):
    try:
        chimera_command = f"chimera --nogui {pdb_file1} {pdb_file2} {com_file} >> {output_txt}"
        subprocess.run(chimera_command, shell=True, check=True)
        print(f"Chimera command executed, distances saved in {output_txt}")
    except Exception as e:
        print(f"An error occurred while running Chimera: {e}")

def extract_and_transform_distances(input_file, output_file):
    try:
        with open(output_file, 'w') as outfile:
            outfile.write("attribute: distance\n")
            outfile.write("recipient: atoms\n")

        with open(input_file, 'r') as infile, open(output_file, 'a') as outfile:
            for line in infile:
                if "Distance" in line:
                    parts = line.split()
                    # Keep only columns 3 and 6
                    selected_parts = [parts[2], parts[5]]
                    # Replace the first two characters of column 3 with a tab
                    selected_parts[0] = '\t' + selected_parts[0][2:]
                    # Join parts with a single tab
                    transformed_line = "\t".join(selected_parts)
                    outfile.write(transformed_line + "\n")
        print(f"Lines containing 'Distance' have been successfully extracted and transformed to {output_file}")
    except Exception as e:
        print(f"An error occurred while extracting and transforming distances: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_pdb1> <input_pdb2>")
        sys.exit(1)

    input_pdb1 = sys.argv[1]
    input_pdb2 = sys.argv[2]

    output_pdb1 = 'output1.pdb'
    output_pdb2 = 'output2.pdb'
    pseudo_file = 'Pseudobond.pd'
    output_com = 'output.com'
    output_txt = 'distances.txt'
    attribute_txt = 'attribute.txt'

    extract_atom_lines(input_pdb1, output_pdb1)
    extract_atom_lines(input_pdb2, output_pdb2)
    generate_files(output_pdb1, output_pdb2, pseudo_file, output_com)
    run_chimera(input_pdb1, input_pdb2, output_com, output_txt)
    extract_and_transform_distances(output_txt, attribute_txt)

