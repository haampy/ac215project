import torch

def train_model(model, train_dataloader, val_dataloader, criterion, optimizer, device, num_epochs):
    best_model_wts = None 
    best_val_acc = 0.0     
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        running_corrects = 0

        print(f"\nEpoch {epoch+1}/{num_epochs} start...")
        for inputs, labels in train_dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            running_corrects += (outputs.argmax(1) == labels).sum().item()

        epoch_loss = running_loss / len(train_dataloader.dataset)
        epoch_acc = running_corrects / len(train_dataloader.dataset)

        print(f'Epoch {epoch+1}/{num_epochs}, Train Loss: {epoch_loss:.4f}, Train Acc: {epoch_acc:.4f}')

        model.eval()
        val_loss = 0.0
        val_corrects = 0

        with torch.no_grad():
            for inputs, labels in val_dataloader:
                inputs = inputs.to(device)
                labels = labels.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * inputs.size(0)
                val_corrects += (outputs.argmax(1) == labels).sum().item()

        val_epoch_loss = val_loss / len(val_dataloader.dataset)
        val_epoch_acc = val_corrects / len(val_dataloader.dataset)

        print(f'Epoch {epoch+1}/{num_epochs}, Val Loss: {val_epoch_loss:.4f}, Val Acc: {val_epoch_acc:.4f}')

        if val_epoch_acc > best_val_acc:
            best_val_acc = val_epoch_acc
            best_model_wts = model.state_dict().copy()  

    if best_model_wts is not None:
        model.load_state_dict(best_model_wts)
        print(f"Best model loaded with Val Acc: {best_val_acc:.4f}")

    return model
