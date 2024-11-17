import hitster_config as c
mm = c.mm

def generate_card_front(canvas, link, x, y):
    # Front side: Black background with white QR code
    canvas.setLineWidth(0)
    canvas.setStrokeColor('white')
    canvas.setFillColor('black')
    canvas.rect(x, y, 64*mm, 64*mm, fill=1)
    # Background: Eight vividly colored circles with openings
    colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFA500", "#800080"]
    circle_count = 8
    circle_radius = 18  # Initial radius of the smallest circle
    opening_percentage = 0.2  # Percentage of the circle missing
    opening_angle = 360 * opening_percentage

    for i in range(circle_count):
        canvas.setFillColor(colors[i])
        canvas.setStrokeColor(colors[i])
        canvas.setLineWidth(1)

        # Calculate the bounding box for the circle
        x1 = 32.5*mm - circle_radius*mm
        y1 = 32.5*mm - circle_radius*mm
        x2 = 32.5*mm + circle_radius*mm
        y2 = 32.5*mm + circle_radius*mm

        randAngle = c.random.randint(0, 360)
        # Draw an arc to create the opening in the circle
        canvas.arc(x + x1, y + y1, x + x2, y + y2, randAngle, 360 - opening_angle)

        circle_radius += 1.5  # Increase the radius for the next circle

    qr = c.qrcode.QRCode(version=1, error_correction=c.qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="black")
    canvas.drawInlineImage(img, x + 20*mm, y + 20*mm, width=24*mm, height=24*mm)
    
def generate_card_back(canvas, artist, title, year, x , y):
    canvas.setLineWidth(0)  # Set line width to 0 to remove the border
    gradient_height = 64
    num_sections = 100  # Adjust the number of sections for the gradient
    section_height = gradient_height / num_sections
    start_color = (
        (c.random.random() * 0.5) + 0.4,  # Red component between 0.6 and 1.0
        (c.random.random() * 0.5) + 0.4,  # Green component between 0.6 and 1.0
        (c.random.random() * 0.5) + 0.4   # Blue component between 0.6 and 1.0
    )

    # Simulated color gradient background with text
    for i in range(num_sections):
        for j in range(num_sections):
            color_ratio_i = i / num_sections
            color_ratio_j = j / num_sections
            gradient_color = (start_color[0] + color_ratio_i * 0.5 + color_ratio_j * 0.5, start_color[1] + color_ratio_i * 0.1, start_color[2] + color_ratio_j * 0.1)
            canvas.setFillColorRGB(*gradient_color)
            canvas.setStrokeColorRGB(*gradient_color)
            canvas.rect(x + j * section_height * mm, y + i * section_height * mm, section_height * mm, section_height * mm, fill=1)

    # Text
    canvas.setFillColor('black')  # Set text color to black
    canvas.setFont("Helvetica-Bold", 10)  # Bold artist text, 7mm away from top
    canvas.drawCentredString(x + 32.5*mm, y + 53*mm, artist)

    canvas.setFont("Helvetica-Bold", 46)  # Year text, centered and bold
    canvas.drawCentredString(x + 32.5*mm, y + 26*mm, str(year))

    canvas.setFont("Helvetica-Oblique", 10)  # Italic and not bold title text, 7mm away from bottom
    
    maxL = 32
    if len(title) > maxL:
        titleLines = [title[0:maxL], title[maxL:]]
        canvas.drawCentredString(x + 32.5*mm, y + 8*mm, titleLines[0])
        canvas.drawCentredString(x + 32.5*mm, y + 4*mm, titleLines[1])
    else:
        canvas.drawCentredString(x + 32.5*mm, y + 8*mm, title)

def export():
    if len(c.display_songs) > 0:
        pdf_filename = c.selected_pack_name + '.pdf'
        cWidth = 210*mm
        cHeight = 297*mm
        can = c.canvas.Canvas(pdf_filename, pagesize=(cWidth, cHeight))  # A4 size
        can.setTitle(c.selected_pack_name)
        
        # Define card size and margin
        card_size = 64*mm
        margin = 5*mm

        # Calculate the number of rows and columns for the cards
        num_cols = int((cWidth) // (card_size))
        num_rows = int((cHeight) // (card_size))
        cardsPerPage = min(num_cols * num_rows, len(c.display_songs))
        totalWidth = num_cols * card_size + (num_cols - 1) * margin
        totalHeight = num_rows * card_size + (num_rows - 1) * margin
        baseX = (cWidth - totalWidth) / 2
        baseY = (cHeight - totalHeight) / 2

        nPage = 0
        idx = 0
        for i in range(2 * len(c.display_songs)):
            #print(i)
            isFront = not nPage % 2
            N = min(cardsPerPage, len(c.display_songs) - nPage // 2 * cardsPerPage)

            row = idx // num_cols
            if isFront:
                col = idx % num_cols
            else:
                col = num_cols - 1 - idx % num_cols

            x = baseX + col * card_size + col * margin
            y = baseY + row * card_size + row * margin
            
            #print('page',nPage,'idx',idx,'isFront',isFront,'col',col,'row',row,'N',N)
            
            song = c.display_songs[nPage // 2 * cardsPerPage + idx]
            if isFront:
                generate_card_front(can, song[1], x, y)  # Assuming link is in the second position
                #print("front" + song[3])
            else:
                generate_card_back(can, song[2], song[3], song[4], x, y)  # Artist, title, year positions
                #print("back" + song[3])       

            if idx == N - 1:
                can.showPage()  # Start a new page for each set of cards
                nPage = nPage + 1
                idx = 0
                #print("new page")
            else:
                idx = idx + 1

        can.save()
        # After saving the PDF file:
        c.subprocess.Popen([pdf_filename], shell=True)
        c.messagebox.showinfo("Export Complete", "PDF cards generated successfully!")
    else:
        c.messagebox.showwarning("No Songs", "No songs found to export!")